# CO-502: Upstream Node Unreachable — Runbook

**Document Type:** Runbook
**Last Updated:** 2026-03-15
**Applies To:** All Plans
**Tier:** Tier 2

## Summary

Error CO-502 indicates that the CloudOps control plane cannot reach one or more nodes in your cluster. This typically means a node is down, partitioned from the network, or has exhausted resources and become unresponsive.

## Symptoms

- HTTP 502 response from `api.cloudops.example/v1` for cluster operations
- Nodes listed as `NotReady` in the Web Console cluster view
- Workloads not scheduling or being evicted
- `cloudopsctl cluster nodes list` shows one or more nodes in `NotReady` state

## Diagnostic Steps

### Step 1 — Identify affected nodes

```bash
cloudopsctl cluster nodes list --cluster-id YOUR_CLUSTER_ID
```

Note which nodes show `NotReady`. Multiple nodes unreachable simultaneously suggests a network partition or a node pool scaling issue.

### Step 2 — Review node events

In the Web Console: **Clusters > [Cluster Name] > Nodes > [Node Name] > Events**

Look for:
- `OutOfDisk` or `MemoryPressure` conditions (resource exhaustion)
- `NetworkPlugin` errors (network configuration issues)
- `KubeletNotReady` (node kubelet process is not running)

### Step 3 — Check for co-occurring CO-500

CO-502 often accompanies CO-500. If the control plane itself is also degraded, consult [runbook_co500.md](runbook_co500.md) first.

### Step 4 — Check node pool health

```bash
cloudopsctl nodepool list --cluster-id YOUR_CLUSTER_ID
```

If a node pool is in `SCALING` state, the node may be temporarily unavailable during a scale event. Wait 5 minutes and check again.

## Immediate Mitigation

**Option 1 — Cordon and drain the affected node:**
```bash
cloudopsctl node cordon --cluster-id YOUR_CLUSTER_ID --node-id NODE_ID
cloudopsctl node drain --cluster-id YOUR_CLUSTER_ID --node-id NODE_ID
```
This prevents new workloads from scheduling on the unhealthy node.

**Option 2 — Replace the node:**
```bash
cloudopsctl node replace --cluster-id YOUR_CLUSTER_ID --node-id NODE_ID
```
This terminates the unhealthy node and provisions a replacement. Downtime for workloads on that node until they reschedule.

## Escalation

Escalate to Tier 2 if:
- More than 30% of nodes in a pool are unreachable
- Node replacement fails
- The issue recurs within 24 hours without explanation

Provide: cluster ID, node IDs, and the output of `cloudopsctl cluster diagnose`.

## Related Documents
- [runbook_co500.md](runbook_co500.md)
- [runbook_node_pool_scaling.md](runbook_node_pool_scaling.md)
- [escalation_engineering.md](escalation_engineering.md)
