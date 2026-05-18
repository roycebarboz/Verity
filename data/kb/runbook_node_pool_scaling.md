# Node Pool Scaling Failures — Runbook

**Document Type:** Runbook
**Last Updated:** 2026-03-15
**Applies To:** All Plans
**Tier:** Tier 2

## Summary

This runbook covers failures encountered when scaling a node pool up or down — either manually or via auto-scaling. Scaling failures can result in CO-504 timeouts, CO-601 quota errors, or nodes that are provisioned but fail to join the cluster.

## Symptoms

- Scale-up operation stuck in `SCALING` state for more than 10 minutes
- New nodes provisioned but showing `NotReady` in the cluster node list
- Scale-down operation leaving pods in `Terminating` state indefinitely
- CO-504 returned from a scale operation
- Auto-scaling not triggering despite high resource utilization

## Diagnostic Steps

### Step 1 — Check the scaling operation status

```bash
cloudopsctl operation status --operation-id OPERATION_ID
cloudopsctl nodepool list --cluster-id YOUR_CLUSTER_ID
```

Identify whether the operation completed, timed out, or is still pending.

### Step 2 — Inspect new nodes (scale-up failures)

```bash
cloudopsctl cluster nodes list --cluster-id YOUR_CLUSTER_ID --status NotReady
```

Common reasons nodes fail to become Ready:
- **Node initialization scripts failed:** Check node logs via the Web Console > **Clusters > [Cluster] > Nodes > [Node] > Logs**
- **Networking misconfiguration:** CNI plugin failed to initialize on the node
- **Kubelet not starting:** Usually a node image or version incompatibility

### Step 3 — Check auto-scaling configuration (if using auto-scale)

```bash
cloudopsctl nodepool get --cluster-id YOUR_CLUSTER_ID --pool-id POOL_ID
```

Verify:
- `min_nodes` ≤ current count ≤ `max_nodes`
- `scale_up_threshold` (CPU or memory %) is set correctly
- No `scale_in_protection` is applied to the pool (prevents scale-down)

### Step 4 — Check quota (for scale-up failures)

CO-601 during a scale operation means you've hit your node limit. See [runbook_co601.md](runbook_co601.md).

## Resolution

**Scale-up — nodes stuck NotReady:**
1. Cordon and drain the stuck nodes.
2. Replace them: `cloudopsctl node replace --cluster-id CLUSTER_ID --node-id NODE_ID`

**Scale-down — pods stuck Terminating:**
1. Check for pods with `terminationGracePeriodSeconds` set very high.
2. Force-delete if needed: review your deployment for stuck finalizers.

**Auto-scaling not triggering:**
1. Verify the auto-scaling policy in the Web Console: **Clusters > [Cluster] > Node Pools > [Pool] > Auto-scaling**.
2. Check that `cloudopsctl` and the Web Console show the same pool configuration.

## Escalation

Escalate to Tier 2 if multiple replacement attempts fail, or if the auto-scaling system is not responding to configuration changes after 30 minutes.

## Related Documents
- [runbook_co601.md](runbook_co601.md)
- [runbook_co504.md](runbook_co504.md)
- [feature_auto_scaling.md](feature_auto_scaling.md)
