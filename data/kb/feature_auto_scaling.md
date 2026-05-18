# Auto-Scaling Configuration Guide

**Document Type:** Feature
**Last Updated:** 2026-03-15
**Applies To:** Professional, Enterprise
**Tier:** Tier 1

## Summary

CloudOps Platform supports horizontal auto-scaling of node pools based on CPU and memory utilization. This guide covers how to enable auto-scaling, configure thresholds, and troubleshoot common auto-scaling issues.

## Prerequisites

- Auto-scaling is available on **Professional ($499/mo)** and **Enterprise** plans.
- You must have **Operator** or **Organization Admin** role.

## Enabling Auto-Scaling

### Via the Web Console

1. Log in to [console.cloudops.example](https://console.cloudops.example).
2. Navigate to **Clusters > [Cluster Name] > Node Pools**.
3. Click on the node pool you want to configure.
4. Toggle **Enable Auto-scaling** to ON.
5. Configure the settings:
   - **Minimum nodes:** The floor — auto-scaling will not scale below this count.
   - **Maximum nodes:** The ceiling — auto-scaling will not scale above this count.
   - **Scale-up threshold:** CPU or memory % at which a new node is added (default: 75%).
   - **Scale-down threshold:** CPU or memory % below which a node is removed (default: 40%).
   - **Scale-down delay:** How long utilization must be below the threshold before scale-down triggers (default: 10 minutes).
6. Click **Save**.

### Via the CLI

```bash
cloudopsctl nodepool update \
  --cluster-id YOUR_CLUSTER_ID \
  --pool-id YOUR_POOL_ID \
  --auto-scale true \
  --min-nodes 2 \
  --max-nodes 10 \
  --scale-up-threshold 75 \
  --scale-down-threshold 40 \
  --scale-down-delay 10m
```

## Best Practices

- Set `min-nodes` to at least 2 for high-availability workloads.
- Use separate node pools for different workload types (e.g., one pool for web serving, one for batch jobs) with different auto-scaling configurations.
- Set `scale-down-delay` to at least 5 minutes to avoid thrashing (rapidly scaling up and down).

## Monitoring Auto-Scaling Events

Auto-scaling events are logged in the cluster event stream:
```bash
cloudopsctl cluster events --cluster-id YOUR_CLUSTER_ID --filter auto-scale
```

## Troubleshooting

- **Auto-scaling not triggering:** Verify the node pool has auto-scaling enabled and the threshold is correctly set. Check that the node pool has not hit the `max-nodes` limit.
- **Scaling up but workloads still slow:** Check if workloads have resource requests set too low, causing inaccurate utilization reporting.
- **Scale-down not happening:** Ensure `scale-down-delay` is not set too high. Check for `scale_in_protection` on individual nodes.

See [runbook_node_pool_scaling.md](runbook_node_pool_scaling.md) for failure scenarios.

## Related Documents
- [runbook_node_pool_scaling.md](runbook_node_pool_scaling.md)
- [feature_multi_region.md](feature_multi_region.md)
- [pricing_plan_comparison.md](pricing_plan_comparison.md)
