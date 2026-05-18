# Outage Communication Protocol

**Document Type:** Escalation
**Last Updated:** 2026-03-15
**Applies To:** All Plans
**Tier:** Tier 2

## Summary

This document defines the communication protocol for customer-facing outage notifications during P1 and P2 incidents. It specifies what to communicate, when, and through which channels.

## Communication Principles

- **Communicate early, even with limited information.** A short "we are aware and investigating" message is better than silence.
- **Never speculate on root cause publicly** until it is confirmed.
- **Update at least every 30 minutes** during an active P1 incident.
- **Use plain language.** Avoid technical jargon in customer-facing messages.

## Communication Channels

| Channel | Used For | Managed By |
|---|---|---|
| Status page ([status.cloudops.example](https://status.cloudops.example)) | All incidents; primary source of truth | Incident Commander |
| Email to affected customers | P1 incidents confirmed to affect >10% of customers | Support Lead |
| Web Console banner | Active degradation or maintenance | Incident Commander |
| Slack integration alerts | Automated; fires on any CO-500/CO-503 pattern | Platform automation |

## Notification Timeline

### T+0 — Incident Declared
- Update status page: **"Investigating — [Service Name] Degradation"**
- Web Console banner: **"We are aware of an issue affecting cluster operations. Investigating."**

### T+15 — First Update
- Update status page with what is known (services affected, regions, estimated customers)
- Do not yet state root cause or ETA unless confirmed

### T+30 — Ongoing Update
- If not resolved, post an update confirming investigation is ongoing
- If root cause is identified, state it plainly: "We have identified a configuration issue in the control plane routing layer."

### T+60+ — Every 30 Minutes Until Resolution

### Resolution — Incident Resolved
- Status page: **"Resolved — [Brief description of fix applied]"**
- Email to affected customers: Summary of what happened, duration, and what was done
- Internal: Kick off post-mortem process (see [runbook_outage_postmortem.md](runbook_outage_postmortem.md))

## Message Templates

**Investigating:**
> We are currently investigating an issue affecting [service] in [region(s)]. Customers may experience [brief impact description]. We will provide an update in 30 minutes.

**Identified:**
> We have identified the root cause of the issue affecting [service]: [brief root cause]. We are actively working on a fix and expect resolution by [time] (tentative).

**Resolved:**
> The issue affecting [service] has been resolved as of [time UTC]. Impact lasted approximately [duration]. A post-mortem will be published within 5 business days.

## Related Documents
- [runbook_outage_postmortem.md](runbook_outage_postmortem.md)
- [escalation_engineering.md](escalation_engineering.md)
- [policy_sla.md](policy_sla.md)
