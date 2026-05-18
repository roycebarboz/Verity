# When to Escalate to Tier 2

**Document Type:** Escalation
**Last Updated:** 2026-03-15
**Applies To:** All Plans
**Tier:** Tier 1

## Summary

This guide helps Tier 1 support agents determine when a customer issue must be escalated to the Tier 2 (Cluster Diagnostics & Billing) team. Escalating too early wastes Tier 2 capacity; escalating too late frustrates customers. Use this guide to make the right call.

## Always Escalate Immediately to Tier 2

Escalate immediately without further troubleshooting if any of the following are true:

- **Cluster data loss is suspected** — customer reports data that should be present is missing
- **Security breach reported** — customer believes their cluster or account was accessed without authorization
- **CO-500 persists for more than 15 minutes** and no platform incident is listed on [status.cloudops.example](https://status.cloudops.example)
- **Billing dispute exceeds $500** — disputes above this amount require Tier 2 billing review
- **Customer is Enterprise tier** — Enterprise SLA response times require Tier 2 involvement for P1/P2 issues
- **MFA lockout cannot be resolved through backup codes** — account recovery requires Tier 2 identity verification

## Escalate After Completing Tier 1 Steps

Escalate after completing the relevant runbook steps if:

- CO-401, CO-403, or CO-429 persists after all self-service remediation steps in the runbook are complete
- SSO is not functioning after re-uploading IdP metadata and verifying ACS URL
- Cluster is stuck in `CREATING` or `ERROR` state for more than 20 minutes after a force-restart attempt
- Node replacement (via `cloudopsctl node replace`) fails more than once
- Customer has followed all steps in [runbook_co504.md](runbook_co504.md) and timeouts recur

## Do Not Escalate to Tier 2 For

- Password resets (use [faq_password_reset.md](faq_password_reset.md))
- CO-602 (Invalid Manifest) — always a customer configuration issue
- Plan change or upgrade requests — self-service via the Web Console
- Free trial questions — resolve with [policy_free_trial_terms.md](policy_free_trial_terms.md)
- Questions about pricing — resolve with [pricing_plan_comparison.md](pricing_plan_comparison.md)

## How to Escalate

1. Open the ticket in the support portal.
2. Click **Escalate to Tier 2** and select the escalation reason.
3. Add a concise summary: what the customer reported, what steps were taken, and what the current state is.
4. Attach relevant diagnostic IDs, cluster IDs, and error logs.

## Related Documents
- [escalation_engineering.md](escalation_engineering.md)
- [escalation_legal_compliance.md](escalation_legal_compliance.md)
- [policy_sla.md](policy_sla.md)
