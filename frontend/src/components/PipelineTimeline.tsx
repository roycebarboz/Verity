import AgentCard from './AgentCard'
import { TriageResponse } from '../types'

const AGENT_KEYS = ['bouncer', 'librarian', 'drafter', 'verifier', 'dispatcher'] as const

interface Props {
  result: TriageResponse | null
  loading: boolean
}

export default function PipelineTimeline({ result, loading }: Props) {
  return (
    <section className="flex-1 overflow-y-auto p-stack-lg bg-surface-container-low flex flex-col items-center">
      <div className="w-full max-w-2xl">
        <div className="flex items-center justify-between mb-8">
          <h2 className="font-title-lg text-title-lg">Pipeline Timeline</h2>
        </div>

        {!result && !loading && (
          <div className="flex flex-col items-center justify-center py-24 gap-4 text-on-surface-variant">
            <span className="material-symbols-outlined text-[48px] opacity-30">bolt</span>
            <p className="text-body-md opacity-60">Submit a ticket to see the pipeline run.</p>
          </div>
        )}

        {(result || loading) && (
          <div className="relative space-y-8 pb-12">
            <div className="absolute left-6 top-4 bottom-4 w-0.5 bg-outline-variant z-0" />
            {AGENT_KEYS.map((key) => (
              <AgentCard
                key={key}
                agentKey={key}
                step={result?.pipeline[key] ?? null}
                loading={loading && !result}
                verifierStep={key === 'drafter' ? (result?.pipeline.verifier ?? null) : null}
              />
            ))}
          </div>
        )}
      </div>
    </section>
  )
}
