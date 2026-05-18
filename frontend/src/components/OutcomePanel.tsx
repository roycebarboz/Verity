import { TriageResponse } from '../types'

interface Props {
  result: TriageResponse | null
  loading: boolean
}

function actionStyles(action: string) {
  switch (action) {
    case 'send':
      return { border: 'border-green-500', bg: 'bg-green-500', label: 'Action: SEND' }
    case 'escalate':
      return { border: 'border-red-500', bg: 'bg-red-500', label: 'Action: ESCALATE' }
    case 'request_info':
      return { border: 'border-amber-400', bg: 'bg-amber-400', label: 'Action: REQUEST INFO' }
    default:
      return { border: 'border-outline-variant', bg: 'bg-outline-variant', label: action.toUpperCase() }
  }
}

export default function OutcomePanel({ result, loading }: Props) {
  const styles = result ? actionStyles(result.final_action) : null

  return (
    <aside className="w-[450px] flex flex-col p-stack-lg bg-surface-container-lowest border-l border-outline-variant">
      <div className="flex items-center gap-2 mb-stack-lg flex-shrink-0">
        <span className="material-symbols-outlined text-primary">analytics</span>
        <h2 className="font-title-lg text-title-lg">Final Outcome</h2>
      </div>

      {!result && !loading && (
        <div className="flex flex-col items-center justify-center flex-1 gap-4 text-on-surface-variant">
          <span className="material-symbols-outlined text-[48px] opacity-30">analytics</span>
          <p className="text-body-md opacity-60">Results will appear here.</p>
        </div>
      )}

      {loading && !result && (
        <div className="flex flex-col items-center justify-center flex-1 gap-4 text-on-surface-variant">
          <span className="material-symbols-outlined text-[40px] text-secondary animate-pulse">hourglass_top</span>
          <p className="text-body-md">Running pipeline…</p>
        </div>
      )}

      {result && styles && (
        <div className="space-y-stack-lg overflow-y-auto flex-1">
          {/* Decision */}
          <div className={`p-6 rounded-xl border-l-8 ${styles.border} bg-surface-container-low border`}>
            <label className="font-label-md text-label-md text-on-surface-variant uppercase block mb-2">Decision</label>
            <span className={`px-6 py-2 ${styles.bg} text-white font-black text-headline-sm rounded-lg inline-block`}>
              {styles.label}
            </span>
          </div>

          {/* Final Response */}
          <div className="flex flex-col gap-2">
            <label className="font-label-md text-label-md text-on-surface-variant uppercase">Final Response</label>
            <div className="p-5 rounded-xl bg-surface-container-lowest border border-outline-variant text-body-md text-on-surface leading-relaxed shadow-sm">
              {result.final_response || <span className="text-on-surface-variant italic">No response text.</span>}
            </div>
          </div>

          {/* Citations */}
          {result.citations.length > 0 && (
            <div className="flex flex-col gap-3">
              <label className="font-label-md text-label-md text-on-surface-variant uppercase">Citations</label>
              <div className="flex flex-wrap gap-2">
                {result.citations.map((c, i) => (
                  <div
                    key={i}
                    className="flex items-center gap-2 px-3 py-1.5 bg-surface-container-low border border-outline-variant rounded-full text-on-surface-variant text-body-sm hover:bg-secondary-container hover:text-on-secondary-container transition-colors cursor-help"
                    title={c.doc_title}
                  >
                    <span className="material-symbols-outlined text-[16px]">description</span>
                    {c.source}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Verifier Reasoning */}
          {result.pipeline.verifier.output.verifier_passed !== undefined && (
            <div className="flex flex-col gap-2">
              <label className="font-label-md text-label-md text-on-surface-variant uppercase">Verifier Reasoning</label>
              <div className="p-4 rounded-xl bg-surface-container-low border border-outline-variant text-body-sm text-on-surface-variant leading-relaxed">
                {result.pipeline.verifier.output.verifier_passed
                  ? `Verification passed. Citation coverage: ${typeof result.pipeline.verifier.output.citation_coverage === 'number' ? (result.pipeline.verifier.output.citation_coverage as number).toFixed(3) : '—'}. No PII detected.`
                  : `Verification failed after ${result.pipeline.drafter.attempt} attempt(s). Reasons: ${(result.pipeline.verifier.output.verifier_failure_reasons as string[] ?? []).join(', ') || 'none recorded'}.`
                }
              </div>
            </div>
          )}
        </div>
      )}
    </aside>
  )
}
