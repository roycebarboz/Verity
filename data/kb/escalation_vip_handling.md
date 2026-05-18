# VIP Customer Handling Guide

**Document Type:** Escalation
**Last Updated:** 2026-03-15
**Applies To:** Enterprise
**Tier:** Tier 1

## Summary

VIP customers are Enterprise-tier customers who have been flagged for white-glove handling due to their contract value, public profile, or strategic importance to CloudOps. This guide explains how to identify VIP customers and the additional care required when handling their tickets.

## Identifying VIP Customers

A customer is designated VIP if their account is tagged `vip: true` in the support portal CRM. VIP accounts are typically:
- Enterprise contracts exceeding $50,000/year
- Publicly visible logos used in CloudOps marketing (with permission)
- Strategic partners or design partners on the product roadmap

The VIP tag is visible in the customer profile header when you open any ticket from that account.

## VIP Handling Standards

### Response Times
VIP customers are held to tighter internal targets than the standard Enterprise SLA:

| Severity | Target (External SLA) | VIP Internal Target |
|---|---|---|
| P1 | 30 minutes | 15 minutes |
| P2 | 1 hour | 30 minutes |
| P3 | 4 business hours | 2 business hours |
| P4 | 1 business day | 4 business hours |

### Communication Standards
- Address the customer by name, not by ticket number.
- Do not use canned responses. Personalize all communications.
- If a ticket will take longer than the VIP internal target, proactively notify the customer with a status update before the target expires.
- Copy the assigned Customer Success Manager (CSM) on all replies to VIP tickets.

### Escalation
- For any P1 or P2 issue from a VIP customer, notify the CSM and the Support Lead immediately — do not wait for the customer to follow up.
- Escalate to Tier 2 at the first sign of complexity. Do not spend more than 15 minutes troubleshooting a VIP P1 ticket before escalating.

## After Resolution

After resolving a VIP ticket:
- Send a personalized follow-up email within 24 hours confirming resolution and asking if any other assistance is needed.
- Log the resolution summary in the CRM account notes.
- Notify the CSM of the resolution and any signals about customer satisfaction.

## Related Documents
- [escalation_tier2.md](escalation_tier2.md)
- [policy_sla.md](policy_sla.md)
- [escalation_outage_communication.md](escalation_outage_communication.md)
