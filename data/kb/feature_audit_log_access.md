# Audit Log Access — Feature Guide

**Document Type:** Feature
**Last Updated:** 2026-03-15
**Applies To:** Professional, Enterprise
**Tier:** Tier 1

## Summary

The CloudOps Platform audit log provides a tamper-evident record of all administrative actions performed within your organization. This guide covers how to access audit logs, what is logged, available filters, and how to integrate audit logs with external SIEM tools.

## What Is Logged

Every action that modifies state or accesses sensitive resources is logged, including:

| Action Category | Examples |
|---|---|
| Authentication events | Login, logout, failed login, SSO events, MFA changes |
| Cluster operations | Create, delete, scale, restart, backup, restore |
| Deployment operations | Deploy manifest, rollback, delete workload |
| Team and access | Invite member, remove member, role change, transfer ownership |
| API key management | Create key, revoke key, key used (sampled) |
| Billing events | Plan change, payment method update, invoice paid |
| Admin events | SSO configuration change, policy update |

## Accessing Audit Logs

### Web Console
Navigate to [console.cloudops.example](https://console.cloudops.example) > **Admin > Audit Logs**

Available filters:
- Date range
- Actor (by email)
- Action type
- Resource ID (cluster, member, etc.)
- Result (success / failure)

### CLI
```bash
cloudopsctl audit-log list \
  --from 2026-03-01 \
  --to 2026-03-15 \
  --actor user@example.com \
  --action cluster.delete \
  --format json
```

### API
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.cloudops.example/v1/audit-logs?from=2026-03-01&to=2026-03-15&action=cluster.delete"
```

## Log Retention

| Plan | Retention |
|---|---|
| Professional | 90 days |
| Enterprise | 1 year (configurable up to 3 years) |

See [policy_data_retention.md](policy_data_retention.md).

## SIEM Integration

Audit logs can be streamed in real-time to an external SIEM:
1. Navigate to **Admin > Audit Logs > Streaming**.
2. Choose your destination: **S3 bucket**, **Splunk HEC**, **Datadog**, or **generic webhook**.
3. Configure the destination and click **Enable Streaming**.

## Exporting Logs

See [faq_data_export.md](faq_data_export.md) for export instructions.

## Related Documents
- [faq_audit_logs.md](faq_audit_logs.md)
- [faq_data_export.md](faq_data_export.md)
- [feature_iam_rbac.md](feature_iam_rbac.md)
