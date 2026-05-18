# CO-500: Internal Cluster Error — Runbook

**Document Type:** Runbook
**Last Updated:** 2026-03-15
**Applies To:** All Plans
**Tier:** Tier 2

## Summary

Error CO-500 indicates an internal cluster error — an unexpected failure within the managed Kubernetes control plane that requires investigation. This error is typically not caused by the customer's configuration; it signals an issue within the CloudOps infrastructure.

## Symptoms

- HTTP 500 response from `api.cloudops.example/v1`
- "Internal cluster error (CO-500)" displayed in the Web Console
- Cluster shows status `DEGRADED` or `ERROR` in the cluster list
- Deployments failing without a clear manifest-level error
- PagerDuty alert fired for the affected cluster (if configured)

## Diagnostic Steps

### Step 1 — Check platform status

Before troubleshooting, confirm whether this is a platform-wide issue:

1. Visit [status.cloudops.example](https://status.cloudops.example).
2. Check the **Cluster Control Plane** service status.
3. If an incident is active, subscribe to updates. No further action is needed on your end during a platform incident.

### Step 2 — Collect cluster diagnostic information

```bash
cloudopsctl cluster diagnose --cluster-id YOUR_CLUSTER_ID
```

This command collects a diagnostic bundle and returns a `diagnostic_id`. Share this ID when contacting support.

### Step 3 — Check recent cluster events

In the Web Console: **Clusters > [Cluster Name] > Events**

Look for events in the last 30 minutes that precede the CO-500. Common triggers:
- Node pool scaling operations that timed out
- Control plane version upgrade in progress
- Unusual resource quota spikes

### Step 4 — Check for correlated CO-502 errors

CO-500 often accompanies CO-502 (upstream node unreachable). Check whether specific nodes are marked `NotReady`:

```bash
cloudopsctl cluster nodes list --cluster-id YOUR_CLUSTER_ID
```

## Immediate Mitigation

If the cluster is needed urgently:
1. Try a control plane restart: **Clusters > [Cluster Name] > Actions > Restart Control Plane**. (This takes 2–5 minutes and does not affect running workloads.)
2. If that fails, open a P1 ticket with the diagnostic ID.

## Escalation

CO-500 should be escalated to Tier 2 if it persists more than 15 minutes and is not covered by an active platform incident. Include:
- Cluster ID
- `diagnostic_id` from `cloudopsctl cluster diagnose`
- Timestamp of first occurrence
- Any recent changes made to the cluster

If Tier 2 determines this is an infrastructure-level failure, it is escalated to Tier 3 (Engineering).

## Related Documents
- [runbook_co502.md](runbook_co502.md)
- [escalation_engineering.md](escalation_engineering.md)
- [runbook_cluster_wont_start.md](runbook_cluster_wont_start.md)
