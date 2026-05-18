# How Do I Export My Data?

**Document Type:** FAQ
**Last Updated:** 2026-03-15
**Applies To:** All Plans
**Tier:** Tier 1

## Summary

CloudOps Platform allows you to export your cluster configurations, audit logs, and account data at any time. This article covers available export types, how to initiate them, and how long exports are retained.

## Available Export Types

| Export Type | Format | Available To |
|---|---|---|
| Cluster configuration manifests | YAML | All plans |
| Audit logs | JSON, CSV | Professional, Enterprise |
| Billing history | CSV | All plans |
| Team membership list | CSV | Organization Admins |
| Full account data export (GDPR) | ZIP archive | All plans |

## Steps to Export Cluster Configurations

Using the CLI:
```bash
cloudopsctl cluster export --cluster-id YOUR_CLUSTER_ID --output cluster-config.yaml
```

Or via the Web Console:
1. Navigate to **Clusters > [Your Cluster] > Settings**.
2. Click **Export Configuration**.
3. Select the format and click **Download**.

## Steps to Export Audit Logs

1. Navigate to **Admin > Audit Logs**.
2. Set the date range filter.
3. Click **Export** and select CSV or JSON.
4. The export will be prepared in the background. You will receive an email when ready (usually within 5 minutes).

## Requesting a Full GDPR Data Export

For a complete export of all personal data associated with your account, follow the process in [policy_privacy_summary.md](policy_privacy_summary.md). These requests are processed within 30 days per GDPR requirements.

## Related Documents
- [faq_delete_account.md](faq_delete_account.md)
- [policy_data_retention.md](policy_data_retention.md)
- [policy_privacy_summary.md](policy_privacy_summary.md)
