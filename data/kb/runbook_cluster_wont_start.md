# Cluster Won't Start — Runbook

**Document Type:** Runbook
**Last Updated:** 2026-03-15
**Applies To:** All Plans
**Tier:** Tier 2

## Summary

This runbook covers the scenario where a CloudOps cluster fails to reach `RUNNING` status after creation or after being restarted. The cluster remains in `CREATING`, `STARTING`, or `ERROR` state indefinitely.

## Symptoms

- Cluster stuck in `CREATING` state for more than 15 minutes
- Cluster status shows `ERROR` immediately after creation
- `cloudopsctl cluster list` shows status `STARTING` for an extended period
- Error CO-500 or CO-504 is associated with the stuck cluster

## Diagnostic Steps

### Step 1 — Check cluster events

```bash
cloudopsctl cluster events --cluster-id YOUR_CLUSTER_ID
```

Look for the last event before the cluster stopped progressing. Common failure events:
- `ControlPlaneStartFailed` — control plane did not initialize
- `NodePoolProvisioningTimeout` — nodes did not join within the expected window
- `InvalidKubernetesVersion` — requested version is unavailable in your region
- `InsufficientCapacity` — the infrastructure zone lacks available compute capacity

### Step 2 — Validate the cluster configuration

Review the cluster's configuration for common mistakes:
```bash
cloudopsctl cluster get --cluster-id YOUR_CLUSTER_ID --format json
```

Check:
- **Kubernetes version:** Must be within the supported range (check [console.cloudops.example/docs/supported-versions](https://console.cloudops.example/docs/supported-versions))
- **Region availability:** Confirm the selected region is operational at [status.cloudops.example](https://status.cloudops.example)
- **Node pool instance type:** Confirm the requested instance type is available in the region

### Step 3 — Check quota

If CO-601 accompanies the failure, you may have exceeded your cluster or node quota. See [runbook_co601.md](runbook_co601.md).

### Step 4 — Attempt a force-restart

If the cluster is in `ERROR` state (not `CREATING`):
1. In the Web Console: **Clusters > [Cluster Name] > Actions > Force Restart**
2. Monitor the Events tab for progress.

## Resolution

| Event | Resolution |
|---|---|
| `ControlPlaneStartFailed` | Force-restart. If it persists, escalate to Tier 2. |
| `NodePoolProvisioningTimeout` | Delete and recreate the cluster. A new attempt usually succeeds. |
| `InvalidKubernetesVersion` | Recreate with a supported version. |
| `InsufficientCapacity` | Try a different region or availability zone. |

## Escalation

Escalate to Tier 2 if:
- The cluster has been stuck for more than 20 minutes
- Two creation attempts have failed with the same configuration
- Force-restart does not resolve `ERROR` state

Provide: cluster ID, region, Kubernetes version requested, instance type, and event log output.

## Related Documents
- [runbook_co500.md](runbook_co500.md)
- [runbook_co504.md](runbook_co504.md)
- [runbook_co601.md](runbook_co601.md)
