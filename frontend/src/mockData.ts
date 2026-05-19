import { PipelineDoneEvent } from './types'

export const MOCK_RESULT: PipelineDoneEvent = {
  ticket_id: 'tkt_20260518_a3f9',
  dd_trace_id: 'dd_392_8f22_99x1',
  pipeline: {
    bouncer: {
      model: 'gpt-4.1-nano',
      latency_ms: 2954,
      tokens: 358,
      attempt: 1,
      output: { category: 'billing', severity: 'medium', injection_detected: false },
    },
    librarian: {
      model: 'gpt-4.1-nano',
      latency_ms: 3108,
      tokens: 198,
      attempt: 1,
      output: { retrieved_chunks: [{}, {}, {}, {}, {}], queries: ['refund policy', 'billing dispute', 'invoice'] },
    },
    drafter: {
      model: 'gpt-4.1-mini',
      latency_ms: 18225,
      tokens: 3480,
      attempt: 2,
      output: {
        draft_attempts: 2,
        draft_response: 'Thank you for reaching out...',
      },
    },
    verifier: {
      model: 'gpt-5-mini',
      latency_ms: 14691,
      tokens: 3388,
      attempt: 2,
      output: {
        verifier_passed: true,
        pii_detected: false,
        citation_coverage: 0.714,
        verifier_failure_reasons: ['citation_coverage below threshold (0.58 < 0.70)'],
      },
    },
    dispatcher: {
      model: 'gpt-4.1-nano',
      latency_ms: 1718,
      tokens: 700,
      attempt: 1,
      output: { final_action: 'send', reasoning: 'Verifier passed, low severity' },
    },
  },
  final_action: 'send',
  final_response:
    'Thank you for reaching out regarding the apparent double charge on your subscription. To address billing disputes such as this, please follow the dispute process outlined in our Invoice Dispute Process documentation. Typically, credit for disputed amounts appears on your next invoice as a Billing Credit. You can initiate a refund request by navigating to Settings > Billing > Invoices in the Web Console and clicking "Request Refund" on the relevant invoice.',
  citations: [
    { source: 'pricing_invoice_dispute.md', doc_title: 'Invoice Dispute Process', chunk_index: 0, content: '', score: 0.92 },
    { source: 'policy_refund.md', doc_title: 'Refund Policy', chunk_index: 1, content: '', score: 0.88 },
    { source: 'runbook_co701.md', doc_title: 'Runbook CO-701', chunk_index: 0, content: '', score: 0.75 },
  ],
  metrics: {
    total_latency_ms: 32582,
    total_tokens: 6503,
    estimated_cost_usd: 0.00682,
  },
}
