export interface RetrievedChunk {
  content: string
  source: string
  doc_title: string
  chunk_index: number
  score: number
}

export interface AgentStepResult {
  model: string
  latency_ms: number
  tokens: number
  output: Record<string, unknown>
  attempt: number
}

export interface PipelineMetrics {
  total_latency_ms: number
  total_tokens: number
  estimated_cost_usd: number
}

export interface TriageResponse {
  ticket_id: string
  dd_trace_id: string | null
  pipeline: {
    bouncer: AgentStepResult
    librarian: AgentStepResult
    drafter: AgentStepResult
    verifier: AgentStepResult
    dispatcher: AgentStepResult
  }
  final_action: 'send' | 'escalate' | 'request_info'
  final_response: string
  citations: RetrievedChunk[]
  metrics: PipelineMetrics
}

export interface PresetTicket {
  ticket_id: string
  ticket_text: string
  label: string
  icon: string
  iconColor: string
}
