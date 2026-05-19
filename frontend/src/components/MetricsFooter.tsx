import { useState } from 'react'
import { PipelineDoneEvent } from '../types'

interface Props {
  result: PipelineDoneEvent | null
}

export default function MetricsFooter({ result }: Props) {
  const [copied, setCopied] = useState(false)

  function copyTrace() {
    if (!result?.dd_trace_id) return
    navigator.clipboard.writeText(result.dd_trace_id).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    })
  }

  return (
    <footer className="flex justify-between items-center px-margin-page h-12 bg-surface-container-lowest border-t border-outline-variant z-50 flex-shrink-0">
      <div className="flex items-center gap-8">
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-black text-outline uppercase tracking-widest">Total Latency</span>
          <span className="font-mono text-code-sm text-secondary font-bold">
            {result ? `${Math.round(result.metrics.total_latency_ms).toLocaleString()}ms` : '—'}
          </span>
        </div>
        <div className="flex items-center gap-2 border-l border-outline-variant pl-8">
          <span className="text-[10px] font-black text-outline uppercase tracking-widest">Tokens</span>
          <span className="font-mono text-code-sm font-bold">
            {result ? result.metrics.total_tokens.toLocaleString() : '—'}
          </span>
        </div>
        <div className="flex items-center gap-2 border-l border-outline-variant pl-8">
          <span className="text-[10px] font-black text-outline uppercase tracking-widest">Est. Cost</span>
          <span className="font-mono text-code-sm font-bold text-on-surface">
            {result ? `$${result.metrics.estimated_cost_usd.toFixed(5)}` : '—'}
          </span>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {result?.dd_trace_id && (
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-black text-outline uppercase tracking-widest">Trace ID</span>
            <span className="font-mono text-code-sm text-on-surface-variant">{result.dd_trace_id}</span>
            <button onClick={copyTrace} title="Copy trace ID">
              <span className="material-symbols-outlined text-[16px] text-outline cursor-pointer hover:text-primary transition-colors ml-1">
                {copied ? 'check' : 'content_copy'}
              </span>
            </button>
          </div>
        )}
      </div>
    </footer>
  )
}
