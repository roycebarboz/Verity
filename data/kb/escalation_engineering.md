# When to Escalate to Engineering (Tier 3)

**Document Type:** Escalation
**Last Updated:** 2026-03-15
**Applies To:** All Plans
**Tier:** Tier 2

## Summary

This guide defines the criteria for escalating a customer issue from Tier 2 support to the Engineering team (Tier 3). Engineering escalations should be rare and reserved for issues that are confirmed infrastructure failures, data loss events, or security incidents that cannot be resolved through standard support tooling.

## Escalate to Engineering Immediately (P1)

Do not wait — escalate directly if:
- **Active data loss** — a customer's cluster data is being deleted unexpectedly or is inaccessible
- **Active security breach** — confirmed unauthorized access to platform infrastructure or cross-customer data exposure
- **Platform-wide outage** — the Cluster Control Plane API is returning 5xx for all customers, no active incident on status page
- **Backup restoration failure** — `cloudopsctl backup restore` fails after two attempts and data recovery is at risk

## Escalate to Engineering After Tier 2 Investigation

Escalate after completing Tier 2 diagnostics if:
- CO-500 or CO-502 errors persist after control plane restart and node replacement
- A cluster remains stuck in `ERROR` state after all Tier 2 remediation steps are exhausted
- Auto-scaling system is not responding to configuration changes after 30+ minutes of investigation
- A suspected platform bug is identified — behavior not matching documented API contracts
- Performance degradation cannot be attributed to resource saturation (all metrics look normal but response times are elevated)

## Engineering Escalation Is NOT For

- Billing disputes — handle at Tier 2
- CO-602 errors — always a customer manifest issue
- CO-429 rate limit requests — handle at Tier 2 with temporary limit increase if justified
- Feature requests — collect and submit through the product feedback portal
- Questions about roadmap — engineering does not field these through support

## How to Escalate to Engineering

1. In the support portal, escalate the ticket to Tier 2 first (if not already done).
2. From a Tier 2 ticket, click **Escalate to Engineering**.
3. Fill out the Engineering escalation form:
   - **Confirmed customer impact** (data loss, outage, degraded)
   - **Diagnostic ID** from `cloudopsctl cluster diagnose`
   - **Cluster ID(s)** and region
   - **Timeline** of events and actions taken
   - **All error codes observed**
   - **Why Tier 2 steps were insufficient**

4. For P1 (active data loss or breach), also page the on-call engineer directly via PagerDuty policy `cloudops-engineering-oncall`.

## Related Documents
- [escalation_tier2.md](escalation_tier2.md)
- [escalation_outage_communication.md](escalation_outage_communication.md)
- [runbook_backup_restoration.md](runbook_backup_restoration.md)
