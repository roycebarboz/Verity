Junior FDE Pre-screening Assignment
Design and Implementation of a Multi-Agent System
Public GitHub Link Submission: Wednesday, May 20
th at 11:59 PM ET, via e-mail to
tyler.parks@wipro.com
In-Person Presentation: Thursday, May 21st at 1:30 PM ET, virtual presentation
Objectives
The goal of this assignment is to design and implement a live multi-agent system
that demonstrates agent collaboration, task decomposition, and safe use of AI/LLMs. You
will focus on architecture, security guardrails, and implementation strategy, rather than
only model output.
• You may use your choice of AI/LLMs, foundation models, autonomous agents, or
collaborative agent frameworks.
• You may use any cloud provider (AWS, Azure, or GCP are preferred) to host your
system, which should be accessible via a live internet link (public endpoint,
hosted UI, or API).
• The project must be presented virtually, either:
o Through a live demonstration using the deployed link, or
o Via a recorded video walkthrough showcasing the system, its architecture,
and functionality.
Problem Statement and Use Cases
Design a multi-agent system that collaboratively addresses a non-trivial use
case. For example: wealth management, fraud analysis, information retrieval, daily
planning, decision-making, customer support, data analysis, workflow automation,
research and report generator, software/coding assistance, hiring assistance, or any
comparable real-world system.
The system should consist of multiple specialized agents that interact with each
other to achieve a shared goal. You are encouraged to be creative, but designs must be
realistic and defensible. This open-ended assignment emphasizes “system thinking” over
raw model output.

Requirements
Your submission must address the following areas:

1. Multi-Agent Architecture
   Describe and justify your system design:
   • Number and types of agents (e.g., Planner, Executor, Critic, Security Agent, User
   Interface Agent).
   • Responsibilities and boundaries of each agent.
   • Communication patterns (e.g., message passing, shared memory, orchestration
   layer).
   • Whether agents operate sequentially, in parallel, or hierarchically.
2. Security, Safety, and Guardrails
   Explain how your system addresses security and compliance, including:
   • Input validation and prompt injection protection.
   • Guardrails for LLM usage (role constraints, output filtering, policy enforcement).
   • Data handling considerations (PII, secrets, logging).
   • Measures to prevent unintended agent actions or escalation.
3. Implementation Approach
   Detail how you planned and built the system:
   • Tools, frameworks, or libraries used (e.g., Python, LangChain/LangGraph,
   AutoGen, CrewAI, Semantic Kernel, custom orchestration).
   • How agents are instantiated, coordinated, and terminated.
   • How the system handles errors, retries, and failures.
   • Any evaluation or testing approach used to verify correctness.
4. Use of AI / LLMs and Collaboration
   Explain:
   • How and where LLMs are used (e.g., reasoning, planning, summarization,
   critique).
   • How agents collaborate or negotiate decisions.
   • Trade-offs between autonomy vs. control in your design.

Deliverables
Required:
• In-person presentation of the project.
• Written report (1–2 pages max) covering the sections above.
• Link to a public repository containing any project material (recorded video, writeups, etc.).
o Reply to the e-mail containing this assignment.
Optional:
• Architecture diagram.
• Sample prompts.
• A recorded video walkthrough.
Evaluation Criteria
You and your project will be evaluated on:
• Clarity and soundness of the multi-agent design, including the responsible use of
AI/LLMs.
• Thoughtfulness and practicality of security, guardrails, and implementation
approach.
• Overall coherence and technical depth.
