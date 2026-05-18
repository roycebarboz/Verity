import { useState } from 'react'
import TicketInput from './components/TicketInput'
import PipelineTimeline from './components/PipelineTimeline'
import OutcomePanel from './components/OutcomePanel'
import MetricsFooter from './components/MetricsFooter'
import { TriageResponse } from './types'
import { MOCK_RESULT } from './mockData'

const IS_DEMO = new URLSearchParams(window.location.search).has('demo')

export default function App() {
  const [result, setResult] = useState<TriageResponse | null>(IS_DEMO ? MOCK_RESULT : null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(ticketText: string, customerId: string, channel: string) {
    setLoading(true)
    setError(null)
    setResult(null)

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

      if (!res.ok) {
        const body = await res.text()
        throw new Error(`HTTP ${res.status}: ${body}`)
      }

      const data: TriageResponse = await res.json()
      setResult(data)
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
        <div className="flex flex-col">
          <span className="font-headline-md text-headline-md font-bold text-primary leading-tight">Verity</span>
        </div>
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
        <div className="flex items-center gap-3 px-margin-page py-3 bg-error-container text-on-error-container text-body-sm border-b border-outline-variant">
          <span className="material-symbols-outlined text-[18px]">error</span>
          {error}
        </div>
      )}

      {/* Main content */}
      <main className="flex flex-1 overflow-hidden">
        <TicketInput onSubmit={handleSubmit} loading={loading} />
        <PipelineTimeline result={result} loading={loading} />
        <OutcomePanel result={result} loading={loading} />
      </main>

      <MetricsFooter result={result} />
    </div>
  )
}
