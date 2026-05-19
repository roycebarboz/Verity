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

// Emitted by the backend as each agent finishes
export interface AgentStepEvent {
  agent: string
  step: AgentStepResult
}

// Final SSE event — same shape as the old TriageResponse
export interface PipelineDoneEvent {
  ticket_id: string
  dd_trace_id: string | null
  pipeline: Record<string, AgentStepResult>
  final_action: 'send' | 'escalate' | 'request_info'
  final_response: string
  citations: RetrievedChunk[]
  metrics: PipelineMetrics
}

// Grows incrementally as agent_step events arrive
export type StreamingPipeline = Record<string, AgentStepResult>

export interface PresetTicket {
  ticket_id: string
  ticket_text: string
  label: string
  icon: string
  iconColor: string
}
