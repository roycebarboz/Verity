# How Do I Enable and View Audit Logs?

**Document Type:** FAQ
**Last Updated:** 2026-03-15
**Applies To:** Professional, Enterprise
**Tier:** Tier 1

## Summary

Audit logs record all administrative actions taken within your CloudOps organization — including user logins, cluster changes, billing updates, and permission modifications. This article explains how to access and interpret audit logs.

## Accessing Audit Logs

1. Log in to [console.cloudops.example](https://console.cloudops.example) as an **Organization Admin**.
2. Navigate to **Admin > Audit Logs**.
3. Use the date range picker and filter options to narrow your search.

Alternatively, use the CLI:
```bash
cloudopsctl audit-log list --from 2026-03-01 --to 2026-03-15 --format json
```

Or query the API:
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     "https://api.cloudops.example/v1/audit-logs?from=2026-03-01&to=2026-03-15"
```

## Log Entry Fields

Each audit log entry includes:
- `timestamp` — ISO 8601 timestamp
- `actor` — Email of the user who performed the action
- `action` — Action code (e.g., `cluster.delete`, `member.invite`, `billing.update`)
- `resource_id` — ID of the affected resource
- `ip_address` — Source IP
- `result` — `success` or `failure`

## Retention

Audit logs are retained for **90 days** on Professional plans and **1 year** on Enterprise plans. See [policy_data_retention.md](policy_data_retention.md).

## Exporting Audit Logs

See [faq_data_export.md](faq_data_export.md) for export instructions.

## Related Documents
- [feature_audit_log_access.md](feature_audit_log_access.md)
- [faq_data_export.md](faq_data_export.md)
- [policy_data_retention.md](policy_data_retention.md)
