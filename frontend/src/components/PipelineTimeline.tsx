import AgentCard from './AgentCard'
import { PipelineDoneEvent, StreamingPipeline } from '../types'

const AGENT_KEYS = ['bouncer', 'librarian', 'drafter', 'verifier', 'dispatcher'] as const

interface Props {
  streamingPipeline: StreamingPipeline
  activeAgent: string | null
  finalResult: PipelineDoneEvent | null
  loading: boolean
}

function TimelineLine() {
  return <div className="absolute left-6 top-4 bottom-4 w-0.5 bg-outline-variant z-0" />
}

export default function PipelineTimeline({ streamingPipeline, activeAgent, finalResult, loading }: Props) {
  const hasStreaming = Object.keys(streamingPipeline).length > 0
  const isEmpty = !loading && !finalResult && !hasStreaming && activeAgent === null

  return (
    <section className="flex-1 overflow-y-auto p-stack-lg bg-surface-container-low flex flex-col items-center">
      <div className="w-full max-w-2xl">
        <div className="flex items-center justify-between mb-8">
          <h2 className="font-title-lg text-title-lg">Pipeline Timeline</h2>
        </div>

        {/* Empty state */}
        {isEmpty && (
          <div className="flex flex-col items-center justify-center py-24 gap-4 text-on-surface-variant">
            <span className="material-symbols-outlined text-[48px] opacity-30">bolt</span>
            <p className="text-body-md opacity-60">Submit a ticket to see the pipeline run.</p>
          </div>
        )}

        {/* Streaming: completed cards + active "Thinking…" card */}
        {(hasStreaming || activeAgent !== null) && !finalResult && (
          <div className="relative space-y-8 pb-12">
            <TimelineLine />

            {/* Completed agents in pipeline order */}
            {AGENT_KEYS.filter(k => k in streamingPipeline).map(k => (
              <AgentCard
                key={k}
                agentKey={k}
                step={streamingPipeline[k]}
                loading={false}
                verifierStep={k === 'drafter' ? (streamingPipeline['verifier'] ?? null) : null}
              />
            ))}

            {/* Currently active agent — "Thinking…" placeholder */}
            {activeAgent && (
              <AgentCard
                key={`${activeAgent}-thinking`}
                agentKey={activeAgent}
                step={null}
                loading={true}
              />
            )}
          </div>
        )}

        {/* Final: all 5 cards from pipeline_done event */}
        {finalResult && (
          <div className="relative space-y-8 pb-12">
            <TimelineLine />
            {AGENT_KEYS.filter(k => finalResult.pipeline[k] != null).map(k => (
              <AgentCard
                key={k}
                agentKey={k}
                step={finalResult.pipeline[k] ?? null}
                loading={false}
                verifierStep={k === 'drafter' ? (finalResult.pipeline['verifier'] ?? null) : null}
              />
            ))}
          </div>
        )}
      </div>
    </section>
  )
}
