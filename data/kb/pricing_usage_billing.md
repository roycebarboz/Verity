# Usage-Based Billing Explanation

**Document Type:** Pricing
**Last Updated:** 2026-03-15
**Applies To:** All Plans
**Tier:** Tier 1

## Summary

CloudOps Platform billing is primarily subscription-based (flat monthly or annual fee), but certain usage dimensions may result in additional charges beyond the base plan price. This document explains what is and is not subject to usage-based billing.

## What's Included in the Subscription (No Additional Charge)

- Cluster management and control plane operations (up to plan limits)
- API calls (up to plan rate limit)
- Standard monitoring and alerting
- Support access per plan tier
- Audit logs (per retention limit)

## What May Incur Usage-Based Charges

### Additional Storage

Each plan includes a base storage allocation for persistent volumes:
- Starter: 100 GB included
- Professional: 500 GB included
- Enterprise: Negotiated

Storage beyond the included allocation is billed at **$0.10 per GB per month**, rounded to the nearest GB.

### Outbound Data Transfer

Outbound data transfer from CloudOps clusters to the public internet:
- First 10 GB per month: Included for all plans
- Beyond 10 GB: **$0.09 per GB**

Inbound data transfer and transfer between nodes within a cluster are always free.

### Additional Backup Retention (Professional+)

Professional plan includes 14 days of backup retention. Additional retention is available:
- 30 days: +$25/month per cluster
- 90 days: +$75/month per cluster

Enterprise backup retention is negotiated per contract.

## How Usage Is Measured

Usage is measured in real-time and displayed in the Web Console under **Settings > Billing > Usage**. Usage is billed monthly, included on the same invoice as the subscription fee.

## Avoiding Unexpected Charges

- Set usage alerts in the Web Console: **Settings > Billing > Billing Alerts**
- Monitor storage and data transfer trends in the Billing Usage dashboard

## Related Documents
- [pricing_plan_comparison.md](pricing_plan_comparison.md)
- [pricing_invoice_dispute.md](pricing_invoice_dispute.md)
- [faq_update_payment_method.md](faq_update_payment_method.md)
