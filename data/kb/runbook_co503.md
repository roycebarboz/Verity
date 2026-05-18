# CO-503: Service Temporarily Unavailable — Runbook

**Document Type:** Runbook
**Last Updated:** 2026-03-15
**Applies To:** All Plans
**Tier:** Tier 1

## Summary

Error CO-503 indicates that the CloudOps service or a downstream dependency is temporarily unavailable. This is typically a transient error caused by platform maintenance, a brief outage, or a temporary overload condition.

## Symptoms

- HTTP 503 response from `api.cloudops.example/v1`
- "Service temporarily unavailable (CO-503)" in the Web Console
- `cloudopsctl` commands failing with CO-503
- Cluster deployments not responding

## Diagnostic Steps

### Step 1 — Check platform status page

This is always the first step for CO-503:

1. Visit [status.cloudops.example](https://status.cloudops.example).
2. Check the current status of all services (API, Web Console, Cluster Control Plane).
3. If a degradation or outage is listed, subscribe to updates and wait. No action needed on your end.

### Step 2 — Check for scheduled maintenance

Scheduled maintenance windows are announced 48 hours in advance via:
- Email to the Organization Owner
- Banner in the Web Console
- Entry on the status page

Navigate to [status.cloudops.example/maintenance](https://status.cloudops.example/maintenance) to view upcoming windows.

### Step 3 — Retry with backoff

CO-503 is often transient (lasting under 2 minutes). Implement a retry strategy:

```bash
# Simple shell retry example
for i in {1..3}; do
  cloudopsctl cluster list && break || sleep $((i * 10))
done
```

For API integrations, honor the `Retry-After` header if present.

### Step 4 — Isolate whether it's your cluster or the platform

Try accessing a different cluster or performing a different API operation. If only one cluster is affected, the issue may be cluster-specific (check [runbook_co500.md](runbook_co500.md)). If all operations fail, it's a platform issue.

## Resolution

| Scenario | Action |
|---|---|
| Platform-wide outage | Wait for platform recovery. Subscribe to status updates. |
| Cluster-specific | Follow [runbook_co500.md](runbook_co500.md). |
| Maintenance window | Wait for maintenance to complete. |
| Persists > 15 minutes, no status page entry | File a P1 support ticket. |

## Escalation

If CO-503 persists for more than 15 minutes with no corresponding status page entry, file a P1 support ticket immediately. Include: timestamp of first occurrence, affected cluster IDs, and exact API endpoint or action failing.

## Related Documents
- [runbook_co500.md](runbook_co500.md)
- [runbook_co504.md](runbook_co504.md)
- [escalation_outage_communication.md](escalation_outage_communication.md)
