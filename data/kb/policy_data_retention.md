# Data Retention Policy

**Document Type:** Policy
**Last Updated:** 2026-03-15
**Applies To:** All Plans
**Tier:** Tier 1

## Summary

This document describes how long CloudOps Inc. retains different categories of customer data, when data is deleted, and how customers can request early deletion.

## Data Retention Schedule

| Data Type | Starter | Professional | Enterprise |
|---|---|---|---|
| Cluster configurations | 30 days post-cancellation | 30 days post-cancellation | 90 days post-cancellation |
| Persistent volume data | 30 days post-cancellation | 30 days post-cancellation | 90 days post-cancellation |
| Audit logs | 30 days | 90 days | 1 year |
| Billing records | 7 years (tax compliance) | 7 years | 7 years |
| Support ticket history | 2 years | 2 years | 2 years |
| Account metadata | 30 days post-deletion request | 30 days post-deletion request | 30 days |

## Active Subscription Retention

While your subscription is active, all cluster data and configurations are retained indefinitely. Audit logs follow the retention schedule above regardless of subscription status.

## Post-Cancellation Retention

After cancellation, a **30-day grace period** (90 days for Enterprise) applies during which:
- Cluster data is preserved in a stopped state
- The account can be reactivated and data restored

After the grace period, all cluster and workload data is **permanently deleted**. Billing records are retained separately for legal and tax compliance.

## Backup Retention

On-demand and scheduled backups:
- **Starter:** Not available
- **Professional:** Retained for 14 days per backup
- **Enterprise:** Configurable retention, up to 365 days

See [feature_backup_scheduling.md](feature_backup_scheduling.md).

## Personal Data Retention

Personal data (name, email, account information) is retained for the duration of the account plus **30 days** post-account deletion. GDPR erasure requests are honored within 30 days and may result in earlier deletion.

## Requesting Early Deletion

To request deletion of your data before the retention period expires, submit a GDPR erasure request as described in [faq_gdpr_data_request.md](faq_gdpr_data_request.md).

## Related Documents
- [policy_privacy_summary.md](policy_privacy_summary.md)
- [faq_gdpr_data_request.md](faq_gdpr_data_request.md)
- [faq_delete_account.md](faq_delete_account.md)
