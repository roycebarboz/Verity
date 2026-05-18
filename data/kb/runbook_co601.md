# CO-601: Cluster Quota Exceeded — Runbook

**Document Type:** Runbook
**Last Updated:** 2026-03-15
**Applies To:** All Plans
**Tier:** Tier 1

## Summary

Error CO-601 indicates that your account has reached its plan-level cluster or resource quota. New clusters cannot be created, and in some cases, existing clusters cannot scale, until quota is freed or the plan is upgraded.

## Symptoms

- HTTP 400 response with `error_code: CO-601` when creating a new cluster
- "Cluster quota exceeded" message in the Web Console
- `cloudopsctl cluster create` returning: `Error: CO-601 — cluster quota exceeded`
- Node pool scaling blocked with CO-601

## Quota Limits by Plan

| Plan | Max Clusters | Max Node Pools per Cluster | Max Nodes per Pool |
|---|---|---|---|
| Starter ($99/mo) | 3 | 3 | 5 |
| Professional ($499/mo) | 20 | 10 | 50 |
| Enterprise (custom) | Unlimited | Unlimited | Negotiated |

## Diagnostic Steps

### Step 1 — Check current quota usage

In the Web Console: **Settings > Billing > Quota Usage**

Or via CLI:
```bash
cloudopsctl quota list
```

This shows usage vs. limits for clusters, node pools, and nodes.

### Step 2 — Identify unused clusters

Review your cluster list for inactive or development clusters that can be deleted:
```bash
cloudopsctl cluster list --format table
```

Look for clusters with low activity (`last_activity` field) or status `STOPPED`.

### Step 3 — Check for orphaned resources

Sometimes clusters from failed creation attempts consume quota without appearing in the Web Console. Contact support if `cloudopsctl quota list` shows higher usage than visible clusters.

## Resolution

| Root Cause | Resolution |
|---|---|
| Reached cluster limit | Delete unused clusters or upgrade plan. |
| Reached node limit in pool | Delete unused nodes or upgrade plan. |
| Orphaned quota | Contact Tier 1 support to clear orphaned resources. |

### Deleting an Unused Cluster

```bash
cloudopsctl cluster delete --cluster-id CLUSTER_ID --confirm
```

After deletion, quota is freed within 5 minutes.

## Upgrading Your Plan

To increase quota limits, upgrade from Starter to Professional or contact sales for Enterprise:
- Web Console: **Settings > Billing > Subscription > Change Plan**
- See [pricing_plan_comparison.md](pricing_plan_comparison.md)

## Related Documents
- [pricing_plan_comparison.md](pricing_plan_comparison.md)
- [faq_change_plan.md](faq_change_plan.md)
- [runbook_node_pool_scaling.md](runbook_node_pool_scaling.md)
