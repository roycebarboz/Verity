import { Component, ReactNode, useState } from 'react'
import TicketInput from './components/TicketInput'
import PipelineTimeline from './components/PipelineTimeline'
import OutcomePanel from './components/OutcomePanel'
import MetricsFooter from './components/MetricsFooter'
import { AgentStepEvent, PipelineDoneEvent, StreamingPipeline } from './types'
import { MOCK_RESULT } from './mockData'

const IS_DEMO = new URLSearchParams(window.location.search).has('demo')

// Catches render-time exceptions (e.g. unexpected pipeline_done shape) so the
// page degrades gracefully instead of blanking — a stale bundle once crashed
// the whole UI on the bouncer-blocked path.
class RenderErrorBoundary extends Component<{ children: ReactNode }, { error: Error | null }> {
  state = { error: null as Error | null }
  static getDerivedStateFromError(error: Error) { return { error } }
  componentDidCatch(error: Error) { console.error('UI render error:', error) }
  render() {
    if (!this.state.error) return this.props.children
    return (
      <div className="flex items-center gap-3 px-margin-page py-3 bg-error-container text-on-error-container text-body-sm border-b border-outline-variant flex-shrink-0">
        <span className="material-symbols-outlined text-[18px]">error</span>
        Something went wrong rendering this result. Refresh and try again.
      </div>
    )
  }
}

// Mirrors the LangGraph conditional edges — determines which agent runs next.
function nextAgent(agent: string, output: Record<string, unknown>): string | null {
  switch (agent) {
    case 'bouncer':   return output.injection_detected ? 'dispatcher' : 'librarian'
    case 'librarian': return 'drafter'
    case 'drafter':   return 'verifier'
    case 'verifier':  return output.verifier_passed ? 'dispatcher' : 'drafter'
    case 'dispatcher': return null
    default:          return null
  }
}

export default function App() {
  const [streamingPipeline, setStreamingPipeline] = useState<StreamingPipeline>(
    IS_DEMO ? (MOCK_RESULT.pipeline as StreamingPipeline) : {}
  )
  const [activeAgent, setActiveAgent] = useState<string | null>(null)
  const [finalResult, setFinalResult] = useState<PipelineDoneEvent | null>(
    IS_DEMO ? (MOCK_RESULT as PipelineDoneEvent) : null
  )
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(ticketText: string, customerId: string, channel: string) {
    setLoading(true)
    setError(null)
    setStreamingPipeline({})
    setFinalResult(null)
    setActiveAgent('bouncer') // pipeline always opens with Bouncer

    try {
      const res = await fetch('/triage', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ticket_text: ticketText,
          customer_id: customerId,
          channel,
        }),
      })

      if (!res.ok || !res.body) throw new Error(`HTTP ${res.status}`)

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buf = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buf += decoder.decode(value, { stream: true })

        // SSE events are delimited by \n\n
        const parts = buf.split('\n\n')
        buf = parts.pop() ?? '' // keep last incomplete chunk

        for (const raw of parts) {
          const lines = raw.split('\n')
          const eventLine = lines.find(l => l.startsWith('event:'))
          const dataLine  = lines.find(l => l.startsWith('data:'))
          if (!eventLine || !dataLine) continue

          const eventType = eventLine.slice('event:'.length).trim()
          const data      = JSON.parse(dataLine.slice('data:'.length).trim())

          if (eventType === 'agent_step') {
            const { agent, step } = data as AgentStepEvent
            setStreamingPipeline(prev => ({ ...prev, [agent]: step }))
            setActiveAgent(nextAgent(agent, step.output))
          } else if (eventType === 'pipeline_done') {
            setFinalResult(data as PipelineDoneEvent)
            setActiveAgent(null)
          } else if (eventType === 'error') {
            setError((data as { message: string }).message)
          }
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-screen overflow-hidden text-on-surface bg-surface">
      {/* Header */}
      <nav className="flex justify-between items-center w-full px-margin-page h-16 bg-surface-container-highest border-b border-outline-variant flex-shrink-0">
        <span className="font-headline-md text-headline-md font-bold text-primary leading-tight">Verity</span>
        <a
          className="flex items-center gap-2 text-on-surface-variant hover:text-primary transition-colors font-label-md text-label-md"
          href="https://github.com"
          target="_blank"
          rel="noreferrer"
        >
          <span className="material-symbols-outlined text-[18px]">code</span>
          View Repo
        </a>
      </nav>

      {/* Error banner */}
      {error && (
        <div className="flex items-center gap-3 px-margin-page py-3 bg-error-container text-on-error-container text-body-sm border-b border-outline-variant flex-shrink-0">
          <span className="material-symbols-outlined text-[18px]">error</span>
          {error}
        </div>
      )}

      {/* Main content */}
      <RenderErrorBoundary>
        <main className="flex flex-1 overflow-hidden">
          <TicketInput onSubmit={handleSubmit} loading={loading} />
          <PipelineTimeline
            streamingPipeline={streamingPipeline}
            activeAgent={activeAgent}
            finalResult={finalResult}
            loading={loading}
          />
          <OutcomePanel result={finalResult} loading={loading} />
        </main>

        <MetricsFooter result={finalResult} />
      </RenderErrorBoundary>
    </div>
  )
}
