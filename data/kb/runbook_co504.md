# CO-504: Operation Timed Out — Runbook

**Document Type:** Runbook
**Last Updated:** 2026-03-15
**Applies To:** All Plans
**Tier:** Tier 1

## Summary

Error CO-504 indicates that an operation did not complete within the expected time limit. This can occur during cluster provisioning, node pool scaling, deployment rollouts, or backup operations when underlying infrastructure is slow to respond.

## Symptoms

- HTTP 504 response from `api.cloudops.example/v1`
- Operations in the Web Console stuck in `PENDING` status for more than 10 minutes
- `cloudopsctl` commands returning: `Error: CO-504 — operation timed out`
- Cluster creation or scaling stuck in `CREATING` state

## Timeout Thresholds

| Operation | Expected Duration | Timeout |
|---|---|---|
| Cluster creation | 5–8 minutes | 15 minutes |
| Node pool scaling (add nodes) | 3–6 minutes per node | 20 minutes |
| Deployment rollout | 1–5 minutes | 10 minutes |
| Backup creation | 2–15 minutes | 30 minutes |
| Cluster deletion | 5–10 minutes | 20 minutes |

## Diagnostic Steps

### Step 1 — Check the operation status

```bash
cloudopsctl operation status --operation-id OPERATION_ID
```

This returns the current state of any long-running operation. The `OPERATION_ID` is returned when you initiate a cluster or scaling action.

### Step 2 — Review cluster events for the operation

In the Web Console: **Clusters > [Cluster Name] > Events**. Look for events from the time the operation started.

### Step 3 — Check for CO-502 on related nodes

A CO-504 during scaling often indicates that new nodes failed to join the cluster. Check for CO-502 on the new nodes:
```bash
cloudopsctl cluster nodes list --cluster-id YOUR_CLUSTER_ID
```

### Step 4 — Check platform status

Visit [status.cloudops.example](https://status.cloudops.example) for active incidents that may be causing infrastructure latency.

## Resolution

1. **If the operation is stuck in `PENDING`:** Cancel the operation in the Web Console (**Operations > [Operation] > Cancel**) and retry.
2. **If cluster creation timed out:** Delete the partially-created cluster and recreate it.
3. **If scaling timed out:** The partially-scaled node pool may need manual intervention. Contact Tier 2 support.

## Escalation

Escalate to Tier 2 if:
- The timed-out operation cannot be cancelled
- Retrying the same operation produces CO-504 again
- Data or workloads may be impacted

## Related Documents
- [runbook_co502.md](runbook_co502.md)
- [runbook_co500.md](runbook_co500.md)
- [runbook_node_pool_scaling.md](runbook_node_pool_scaling.md)
