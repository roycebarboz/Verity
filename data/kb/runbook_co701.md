# CO-701: Billing Payment Failure — Runbook

**Document Type:** Runbook
**Last Updated:** 2026-03-15
**Applies To:** All Plans
**Tier:** Tier 1

## Summary

Error CO-701 indicates that a billing payment attempt failed. This can occur during the monthly renewal charge, a pro-rated upgrade charge, or a manual invoice payment attempt. Left unresolved, payment failures can lead to service suspension.

## Symptoms

- Email notification from `billing@cloudops.example` with subject "Payment Failed"
- CO-701 error displayed in **Settings > Billing > Invoices**
- Invoice shows status **Payment Failed** in the Web Console
- Warning banner in the Web Console: "Your account has an outstanding payment issue"

## Suspension Timeline

| Days After Failure | Status |
|---|---|
| Day 0 | Payment fails; email notification sent |
| Day 3 | Second automatic retry |
| Day 7 | Third and final automatic retry; second notification sent |
| Day 10 | Account flagged for suspension |
| Day 14 | Cluster access restricted (clusters paused, not deleted) |
| Day 30 | Account suspended; clusters deleted per data retention policy |

## Diagnostic Steps

### Step 1 — Identify the failing invoice

1. Log in to [console.cloudops.example](https://console.cloudops.example).
2. Navigate to **Settings > Billing > Invoices**.
3. Find the invoice marked **Payment Failed** and note the amount and date.

### Step 2 — Verify and update payment method

1. Navigate to **Settings > Billing > Payment Methods**.
2. Verify the card details are current (not expired, correct billing address).
3. If needed, add a new payment method and set it as default. See [faq_update_payment_method.md](faq_update_payment_method.md).

### Step 3 — Retry the payment

1. Return to **Settings > Billing > Invoices**.
2. Click **Retry Payment** on the failed invoice.
3. If successful, the invoice status changes to **Paid** and the account warning banner disappears.

### Step 4 — If retry fails again

Contact your bank to verify:
- The card has not been blocked for international transactions
- There are sufficient funds or credit
- 3D Secure (Verified by Visa / Mastercard SecureCode) is not blocking the charge

## Escalation

If the payment method is valid and retries continue to fail, escalate to Tier 2 billing support with the invoice ID and the last 4 digits of the card on file. Billing disputes over $500 must be escalated to Tier 2.

## Related Documents
- [faq_update_payment_method.md](faq_update_payment_method.md)
- [pricing_invoice_dispute.md](pricing_invoice_dispute.md)
- [policy_cancellation.md](policy_cancellation.md)
