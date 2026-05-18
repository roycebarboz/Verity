# Service Level Agreement (SLA)

**Document Type:** Policy
**Last Updated:** 2026-03-15
**Applies To:** All Plans
**Tier:** Tier 1

## Summary

This document defines the CloudOps Platform uptime commitments, how uptime is measured, what constitutes a qualifying outage, and how SLA credits are calculated and claimed.

## Uptime Commitments

| Plan | Monthly Uptime Commitment |
|---|---|
| Starter ($99/mo) | 99.5% |
| Professional ($499/mo) | 99.9% |
| Enterprise (custom) | 99.95% |

Uptime is measured on a **calendar month** basis, calculated as:
```
Uptime % = (Total minutes - Downtime minutes) / Total minutes × 100
```

## What Counts as Downtime

Downtime is defined as a period during which the CloudOps Cluster Control Plane API (`api.cloudops.example/v1`) is unavailable (returning HTTP 5xx across all endpoints) for more than **2 consecutive minutes**.

The following do **not** count as downtime:
- Scheduled maintenance windows (announced 48 hours in advance)
- Issues caused by customer misconfiguration
- Third-party service outages outside CloudOps control
- Free trial periods

## SLA Credits

If CloudOps fails to meet the uptime commitment in a given month, affected customers are entitled to a service credit:

| Uptime Achieved | Credit |
|---|---|
| 99.0% – below commitment | 10% of monthly fee |
| 95.0% – 98.99% | 25% of monthly fee |
| Below 95.0% | 50% of monthly fee |

Credits apply to future invoices. They are **not** issued as refunds to the original payment method.

## Claiming an SLA Credit

To claim a credit:
1. Submit a support ticket at [support.cloudops.example](https://support.cloudops.example) within **30 days** of the incident.
2. Include: your account ID, the affected dates/times, and the error codes or behavior observed.
3. CloudOps will verify against internal monitoring data and respond within 5 business days.

## Exclusions

Credits will not be issued if:
- The claim is submitted more than 30 days after the qualifying incident
- The account has an outstanding unpaid balance
- The account was suspended at the time of the incident

## Related Documents
- [escalation_outage_communication.md](escalation_outage_communication.md)
- [policy_refund.md](policy_refund.md)
- [runbook_outage_postmortem.md](runbook_outage_postmortem.md)
