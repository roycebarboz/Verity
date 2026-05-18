# Outage Post-Mortem Template — Runbook

**Document Type:** Runbook
**Last Updated:** 2026-03-15
**Applies To:** All Plans
**Tier:** Tier 3

## Summary

This template is used by CloudOps Engineering and Support to document post-mortem analyses following any P1 or P2 incident. A completed post-mortem is published to affected customers within 5 business days of incident resolution.

---

## Incident Summary

| Field | Value |
|---|---|
| Incident ID | INC-XXXXX |
| Severity | P1 / P2 |
| Start Time | YYYY-MM-DDTHH:MM:SSZ |
| End Time | YYYY-MM-DDTHH:MM:SSZ |
| Total Duration | X hours Y minutes |
| Affected Services | [Cluster Control Plane / API / Web Console / etc.] |
| Affected Regions | [us-east-1 / eu-west-1 / etc.] |
| Customers Affected | [Estimated count / All / Specific segment] |

---

## Impact

Describe the customer-facing impact:
- Were clusters unreachable?
- Were deployments failing?
- Were billing operations affected?
- What error codes were observed (CO-500, CO-503, etc.)?

---

## Timeline

| Time (UTC) | Event |
|---|---|
| HH:MM | First alert fired (PagerDuty / Datadog / customer report) |
| HH:MM | Incident commander assigned |
| HH:MM | Root cause identified |
| HH:MM | Mitigation applied |
| HH:MM | Incident resolved |
| HH:MM | Customer communication sent |

---

## Root Cause Analysis

Describe the root cause in plain language. Be specific. Include:
- What failed
- Why it failed
- Why it was not caught before it affected customers

---

## Contributing Factors

List any contributing factors that made the incident worse or harder to resolve:
- Monitoring gaps
- Runbook gaps
- Deployment timing
- External dependencies

---

## Resolution

What steps were taken to resolve the incident? Include both immediate mitigation and the permanent fix.

---

## Action Items

| Action | Owner | Due Date | Status |
|---|---|---|---|
| [Specific improvement] | [Team/person] | YYYY-MM-DD | Open |

---

## Customer Communication

Link to the status page update posted during the incident and the post-mortem summary published to affected customers.

## Related Documents
- [escalation_engineering.md](escalation_engineering.md)
- [escalation_outage_communication.md](escalation_outage_communication.md)
- [policy_sla.md](policy_sla.md)
