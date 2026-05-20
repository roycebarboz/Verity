terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.6"
}

provider "aws" {
  region = var.aws_region
}

# ---------------------------------------------------------------------------
# Variables
# ---------------------------------------------------------------------------

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "ecr_image_uri" {
  type        = string
  description = "Full ECR image URI, e.g. 123456789012.dkr.ecr.us-east-1.amazonaws.com/verity:latest"
}

variable "openai_secret_arn" {
  type        = string
  description = "ARN of the Secrets Manager secret containing the OpenAI API key"
}

variable "dd_secret_arn" {
  type        = string
  description = "ARN of the Secrets Manager secret containing the Datadog API key"
}

variable "dd_site" {
  type    = string
  default = "us5.datadoghq.com"
}

# ---------------------------------------------------------------------------
# Data sources — reuse the default VPC (no NAT gateway; cost containment)
# ---------------------------------------------------------------------------

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# ---------------------------------------------------------------------------
# DynamoDB — audit trail (PAY_PER_REQUEST = $0 at idle)
# ---------------------------------------------------------------------------

resource "aws_dynamodb_table" "audit" {
  name         = "verity-audit"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "ticket_id"

  attribute {
    name = "ticket_id"
    type = "S"
  }

  tags = { Project = "verity" }
}

# ---------------------------------------------------------------------------
# ECR — container registry
# ---------------------------------------------------------------------------

resource "aws_ecr_repository" "verity" {
  name                 = "verity"
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  tags = { Project = "verity" }
}

# ---------------------------------------------------------------------------
# IAM — task execution role (ECS pulls image + reads Secrets Manager)
# ---------------------------------------------------------------------------

data "aws_iam_policy_document" "ecs_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "task_exec" {
  name               = "verity-task-exec"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume.json
}

resource "aws_iam_role_policy_attachment" "task_exec_managed" {
  role       = aws_iam_role.task_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Execution role also needs to read secrets so ECS can inject them as env vars
resource "aws_iam_role_policy" "task_exec_secrets" {
  name = "verity-secrets-read"
  role = aws_iam_role.task_exec.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "secretsmanager:GetSecretValue"
      Resource = [var.openai_secret_arn, var.dd_secret_arn]
    }]
  })
}

# ---------------------------------------------------------------------------
# IAM — task role (runtime: DynamoDB writes + S3 Chroma index reads)
# ---------------------------------------------------------------------------

resource "aws_iam_role" "task" {
  name               = "verity-task"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume.json
}

resource "aws_iam_role_policy" "task_runtime" {
  name = "verity-runtime"
  role = aws_iam_role.task.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["dynamodb:PutItem"]
        Resource = aws_dynamodb_table.audit.arn
      },
      {
        Effect = "Allow"
        Action = ["s3:GetObject", "s3:ListBucket"]
        Resource = [
          "arn:aws:s3:::verity-chroma-index",
          "arn:aws:s3:::verity-chroma-index/*"
        ]
      }
    ]
  })
}

# ---------------------------------------------------------------------------
# Security groups
# ---------------------------------------------------------------------------

resource "aws_security_group" "alb" {
  name        = "verity-alb"
  description = "Allow HTTP inbound to ALB"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Project = "verity" }
}

resource "aws_security_group" "task" {
  name        = "verity-task"
  description = "Allow traffic from ALB to Fargate task on port 8000"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Project = "verity" }
}

# ---------------------------------------------------------------------------
# Application Load Balancer
# ---------------------------------------------------------------------------

resource "aws_lb" "main" {
  name               = "verity-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = data.aws_subnets.default.ids
  idle_timeout       = 120

  tags = { Project = "verity" }
}

resource "aws_lb_target_group" "app" {
  name        = "verity-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = data.aws_vpc.default.id
  target_type = "ip"

  health_check {
    path                = "/health"
    interval            = 30
    timeout             = 10
    healthy_threshold   = 2
    unhealthy_threshold = 3
  }

  tags = { Project = "verity" }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}

# ---------------------------------------------------------------------------
# ECS cluster + CloudWatch logs
# ---------------------------------------------------------------------------

resource "aws_ecs_cluster" "main" {
  name = "verity"
  tags = { Project = "verity" }
}

resource "aws_cloudwatch_log_group" "verity" {
  name              = "/ecs/verity"
  retention_in_days = 7
}

# ---------------------------------------------------------------------------
# ECS task definition
# ---------------------------------------------------------------------------

resource "aws_ecs_task_definition" "app" {
  family                   = "verity"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"   # 0.25 vCPU
  memory                   = "512"   # 512 MB
  execution_role_arn       = aws_iam_role.task_exec.arn
  task_role_arn            = aws_iam_role.task.arn

  container_definitions = jsonencode([{
    name  = "verity"
    image = var.ecr_image_uri

    portMappings = [{
      containerPort = 8000
      protocol      = "tcp"
    }]

    environment = [
      { name = "AWS_REGION",        value = var.aws_region },
      { name = "DYNAMODB_TABLE",    value = aws_dynamodb_table.audit.name },
      { name = "CHROMA_DIR",        value = "/app/data/chroma" },
      { name = "S3_CHROMA_BUCKET",  value = "verity-chroma-index" },
      { name = "DD_LLMOBS_ENABLED", value = "1" },
      { name = "DD_LLMOBS_ML_APP",  value = "verity" },
      { name = "DD_SITE",           value = var.dd_site },
      { name = "DD_SERVICE",        value = "verity-backend" },
      { name = "DD_ENV",            value = "prod" },
    ]

    # Secrets injected at container start — never in logs or console
    secrets = [
      { name = "OPENAI_API_KEY", valueFrom = var.openai_secret_arn },
      { name = "DD_API_KEY",     valueFrom = var.dd_secret_arn },
    ]

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.verity.name
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "ecs"
      }
    }
  }])
}

# ---------------------------------------------------------------------------
# ECS service — one Fargate task behind the ALB
# ---------------------------------------------------------------------------

resource "aws_ecs_service" "app" {
  name            = "verity"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = data.aws_subnets.default.ids
    security_groups  = [aws_security_group.task.id]
    assign_public_ip = true  # required in public subnet without NAT gateway
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = "verity"
    container_port   = 8000
  }

  depends_on = [aws_lb_listener.http]

  tags = { Project = "verity" }
}

# ---------------------------------------------------------------------------
# Outputs
# ---------------------------------------------------------------------------

output "app_url" {
  description = "Public URL of the Verity UI"
  value       = "http://${aws_lb.main.dns_name}"
}

output "ecr_repository_url" {
  description = "ECR URL for pushing new images"
  value       = aws_ecr_repository.verity.repository_url
}

output "dynamodb_table_name" {
  description = "DynamoDB audit table name"
  value       = aws_dynamodb_table.audit.name
}
