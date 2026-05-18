import { AgentStepResult } from '../types'

type AgentStatus = 'pending' | 'running' | 'passed' | 'retry' | 'failed'

interface AgentMeta {
  name: string
  subtitle: string
  icon: string
}

const AGENT_META: Record<string, AgentMeta> = {
  bouncer: { name: 'Bouncer', subtitle: 'Security & Compliance Scan', icon: 'security' },
  librarian: { name: 'Librarian', subtitle: 'Knowledge Retrieval (RAG)', icon: 'menu_book' },
  drafter: { name: 'Drafter', subtitle: 'Response Generation', icon: 'history_edu' },
  verifier: { name: 'Verifier', subtitle: 'Citation & Fact Check', icon: 'fact_check' },
  dispatcher: { name: 'Dispatcher', subtitle: 'Action Routing', icon: 'outgoing_mail' },
}

function statusColors(status: AgentStatus) {
  switch (status) {
    case 'passed':
      return { border: 'border-green-500', icon: 'text-green-500', badge: 'bg-green-100 text-green-700' }
    case 'retry':
      return { border: 'border-amber-400', icon: 'text-amber-400', badge: 'bg-amber-100 text-amber-700' }
    case 'failed':
      return { border: 'border-red-500', icon: 'text-red-500', badge: 'bg-red-100 text-red-700' }
    case 'running':
      return { border: 'border-secondary', icon: 'text-secondary', badge: 'bg-blue-100 text-blue-700' }
    default:
      return { border: 'border-outline-variant', icon: 'text-on-surface-variant', badge: 'bg-surface-container-high text-on-surface-variant' }
  }
}

function fmt(ms: number) {
  return `${Math.round(ms).toLocaleString()}ms`
}

function BouncerOutput({ output }: { output: Record<string, unknown> }) {
  const json = JSON.stringify({
    category: output.category,
    severity: output.severity,
    injection_detected: output.injection_detected,
  })
  return (
    <div className="mt-3 bg-surface-container-low rounded-lg p-2">
      <span className="text-[9px] uppercase text-outline font-bold mb-1 block">Structured Output</span>
      <pre className="font-mono text-[11px] text-on-surface-variant whitespace-pre-wrap break-all">{json}</pre>
    </div>
  )
}

function LibrarianOutput({ output }: { output: Record<string, unknown> }) {
  const chunks = output.retrieved_chunks as unknown[] | null
  return (
    <div className="mt-3 bg-surface-container-low rounded-lg p-2">
      <span className="text-[9px] uppercase text-outline font-bold mb-1 block">Structured Output</span>
      <div className="flex flex-col gap-1">
        <div className="flex justify-between font-mono text-[11px]">
          <span className="text-on-surface-variant">queries:</span>
          <span className="font-bold">generated</span>
        </div>
        <div className="flex justify-between font-mono text-[11px]">
          <span className="text-on-surface-variant">chunks_retrieved:</span>
          <span className="font-bold">{chunks?.length ?? 0}</span>
        </div>
      </div>
    </div>
  )
}

function DrafterOutput({ output, attempt }: { output: Record<string, unknown>; attempt: number }) {
  return (
    <div className="mt-3 bg-surface-container-low rounded-lg p-2">
      <span className="text-[9px] uppercase text-outline font-bold mb-1 block">Structured Output</span>
      <div className="flex justify-between font-mono text-[11px]">
        <span className="text-on-surface-variant">draft_attempts:</span>
        <span className="font-bold">{output.draft_attempts as number ?? attempt}</span>
      </div>
    </div>
  )
}

function VerifierOutput({ output }: { output: Record<string, unknown> }) {
  return (
    <div className="mt-3 bg-surface-container-low rounded-lg p-2">
      <span className="text-[9px] uppercase text-outline font-bold mb-1 block">Structured Output</span>
      <div className="flex flex-col gap-1">
        <div className="flex justify-between font-mono text-[11px]">
          <span className="text-on-surface-variant">passed:</span>
          <span className="font-bold">{String(output.verifier_passed)}</span>
        </div>
        <div className="flex justify-between font-mono text-[11px]">
          <span className="text-on-surface-variant">pii_detected:</span>
          <span className="font-bold">{String(output.pii_detected)}</span>
        </div>
        <div className="flex justify-between font-mono text-[11px]">
          <span className="text-on-surface-variant">citation_coverage:</span>
          <span className="font-bold">{typeof output.citation_coverage === 'number' ? output.citation_coverage.toFixed(3) : '—'}</span>
        </div>
        <div className="flex justify-between font-mono text-[11px]">
          <span className="text-on-surface-variant">failure_reasons:</span>
          <span className="font-bold">{JSON.stringify(output.verifier_failure_reasons ?? [])}</span>
        </div>
      </div>
    </div>
  )
}

function DispatcherOutput({ output }: { output: Record<string, unknown> }) {
  return (
    <div className="mt-3 bg-surface-container-low rounded-lg p-2">
      <span className="text-[9px] uppercase text-outline font-bold mb-1 block">Structured Output</span>
      <div className="flex flex-col gap-1">
        <div className="flex justify-between font-mono text-[11px]">
          <span className="text-on-surface-variant">action:</span>
          <span className="font-bold">"{String(output.final_action)}"</span>
        </div>
      </div>
    </div>
  )
}

function MetaRow({ model, latency, tokens }: { model: string; latency: number; tokens: number }) {
  return (
    <div className="grid grid-cols-3 gap-4 border-t border-outline-variant pt-3 mt-3">
      <div className="flex flex-col">
        <span className="text-[10px] uppercase text-outline font-bold">Model</span>
        <span className="font-mono text-code-sm">{model}</span>
      </div>
      <div className="flex flex-col">
        <span className="text-[10px] uppercase text-outline font-bold">Latency</span>
        <span className="font-mono text-code-sm">{fmt(latency)}</span>
      </div>
      <div className="flex flex-col">
        <span className="text-[10px] uppercase text-outline font-bold">Tokens</span>
        <span className="font-mono text-code-sm">{tokens.toLocaleString()}</span>
      </div>
    </div>
  )
}

interface Props {
  agentKey: string
  step: AgentStepResult | null
  loading: boolean
  verifierStep?: AgentStepResult | null
}

export default function AgentCard({ agentKey, step, loading, verifierStep }: Props) {
  const meta = AGENT_META[agentKey]
  const draftAttempts = agentKey === 'drafter' && step ? (step.output.draft_attempts as number ?? step.attempt) : 1
  // Rejection reasons shown inside the Drafter retry card come from the Verifier step
  const failureReasons: string[] = agentKey === 'drafter'
    ? ((verifierStep?.output.verifier_failure_reasons as string[] | undefined) ?? [])
    : []

  let status: AgentStatus = 'pending'
  if (loading) status = 'running'
  else if (step) {
    if (agentKey === 'bouncer') status = step.output.injection_detected ? 'failed' : 'passed'
    else if (agentKey === 'verifier') status = step.output.verifier_passed ? 'passed' : 'failed'
    else if (agentKey === 'drafter') status = draftAttempts > 1 ? 'retry' : 'passed'
    else status = 'passed'
  }

  const colors = statusColors(status)
  const statusLabel = {
    pending: 'Pending',
    running: 'Running…',
    passed: agentKey === 'bouncer' ? 'Clear'
      : agentKey === 'librarian' ? `${(step?.output.retrieved_chunks as unknown[] | null)?.length ?? 0} Chunks`
      : agentKey === 'drafter' ? 'Drafted'
      : agentKey === 'verifier' ? 'Verified'
      : 'Routed',
    retry: 'Retry',
    failed: agentKey === 'bouncer' ? 'Blocked' : 'Failed',
  }[status]

  const isDrafter = agentKey === 'drafter'
  const hasRetry = isDrafter && step !== null && draftAttempts > 1

  return (
    <div className="relative z-10 flex gap-6">
      <div className={`w-12 h-12 rounded-full bg-surface-container-lowest border-2 ${colors.border} flex items-center justify-center shadow-sm flex-shrink-0`}>
        <span className={`material-symbols-outlined ${colors.icon}`}>{meta.icon}</span>
      </div>

      <div className="flex-1 bg-surface-container-lowest border border-outline-variant rounded-xl overflow-hidden hover:border-secondary transition-all">
        {hasRetry && step ? (
          <>
            {/* Attempt 1 — rejected */}
            <div className="p-4 border-b border-amber-200 bg-amber-50">
              <div className="flex justify-between items-start mb-2">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="font-title-lg text-title-lg">{meta.name}</h3>
                    <span className="text-[10px] bg-amber-100 text-amber-700 px-1.5 py-0.5 rounded font-bold uppercase">Attempt #1</span>
                  </div>
                  <p className="font-label-md text-label-md text-on-surface-variant">{meta.subtitle}</p>
                </div>
                <span className="bg-amber-100 text-amber-700 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-widest">Retry</span>
              </div>
              <div className="grid grid-cols-3 gap-4 border-t border-amber-200 pt-3 mt-3">
                <div className="flex flex-col">
                  <span className="text-[10px] uppercase text-outline font-bold">Model</span>
                  <span className="font-mono text-code-sm">{step.model}</span>
                </div>
                <div className="flex flex-col">
                  <span className="text-[10px] uppercase text-outline font-bold">Latency</span>
                  <span className="font-mono text-code-sm">{fmt(step.latency_ms / draftAttempts)}</span>
                </div>
                <div className="flex flex-col">
                  <span className="text-[10px] uppercase text-outline font-bold">Tokens</span>
                  <span className="font-mono text-code-sm">{Math.round(step.tokens / draftAttempts).toLocaleString()}</span>
                </div>
              </div>
              {failureReasons.length > 0 && (
                <div className="mt-3 bg-amber-100 rounded-lg p-2">
                  <span className="text-[9px] uppercase text-amber-700 font-bold mb-1 block">Verifier Rejection Reason</span>
                  <p className="font-mono text-[11px] text-amber-800">{failureReasons[0]}</p>
                </div>
              )}
            </div>
            {/* Attempt 2 — passed */}
            <div className="p-4">
              <div className="flex justify-between items-start mb-2">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] bg-surface-container-high px-1.5 py-0.5 rounded font-bold uppercase text-on-surface-variant">Attempt #2</span>
                  </div>
                  <p className="font-label-md text-label-md text-on-surface-variant">{meta.subtitle}</p>
                </div>
                <span className="bg-green-100 text-green-700 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-widest">Drafted</span>
              </div>
              <MetaRow model={step.model} latency={step.latency_ms / draftAttempts} tokens={Math.round(step.tokens / draftAttempts)} />
              <DrafterOutput output={step.output} attempt={step.attempt} />
            </div>
          </>
        ) : (
          <div className="p-4">
            <div className="flex justify-between items-start mb-2">
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="font-title-lg text-title-lg">{meta.name}</h3>
                  <span className="text-[10px] bg-surface-container-high px-1.5 py-0.5 rounded font-bold uppercase text-on-surface-variant">
                    {step ? `Attempt #${step.attempt}` : 'Pending'}
                  </span>
                </div>
                <p className="font-label-md text-label-md text-on-surface-variant">{meta.subtitle}</p>
              </div>
              {step && (
                <span className={`${colors.badge} px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-widest`}>
                  {statusLabel}
                </span>
              )}
              {loading && (
                <span className="bg-blue-100 text-blue-700 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-widest animate-pulse">
                  Running…
                </span>
              )}
            </div>
            {step && (
              <>
                <MetaRow model={step.model} latency={step.latency_ms} tokens={step.tokens} />
                {agentKey === 'bouncer' && <BouncerOutput output={step.output} />}
                {agentKey === 'librarian' && <LibrarianOutput output={step.output} />}
                {agentKey === 'drafter' && <DrafterOutput output={step.output} attempt={step.attempt} />}
                {agentKey === 'verifier' && <VerifierOutput output={step.output} />}
                {agentKey === 'dispatcher' && <DispatcherOutput output={step.output} />}
              </>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
