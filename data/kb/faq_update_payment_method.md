# How Do I Update My Payment Method?

**Document Type:** FAQ
**Last Updated:** 2026-03-15
**Applies To:** All Plans
**Tier:** Tier 1

## Summary

You can update your credit card, billing address, or payment details at any time through the Web Console. This article walks through the steps and explains what to do if a payment has already failed.

## Steps to Update Your Payment Method

1. Log in to [console.cloudops.example](https://console.cloudops.example).
2. Navigate to **Settings > Billing > Payment Methods**.
3. Click **Add Payment Method** to add a new card, or click the pencil icon on an existing card to edit it.
4. Enter your card details and billing address.
5. Click **Save**. The new card will be charged on your next billing date.
6. To set a card as the default, click **Set as Default** next to the card.

## If Your Payment Has Already Failed (Error CO-701)

A CO-701 error means a billing payment failure occurred. To resolve:

1. Update your payment method using the steps above.
2. Navigate to **Settings > Billing > Invoices**.
3. Find the outstanding invoice marked **Unpaid**.
4. Click **Retry Payment**.

If payment still fails, contact your bank to confirm that international transactions are not blocked and that the card has sufficient credit.

## Accepted Payment Methods

- Visa, Mastercard, American Express, Discover
- ACH/bank transfer (Enterprise plans only)
- Purchase orders (Enterprise plans only — contact your Account Manager)

## Notes

- CloudOps does not store raw card data. All payment processing is handled by our PCI-compliant payment processor.
- After 3 consecutive failed payment attempts, your account may be suspended.

## Related Documents
- [runbook_co701.md](runbook_co701.md)
- [pricing_invoice_dispute.md](pricing_invoice_dispute.md)
- [policy_cancellation.md](policy_cancellation.md)
