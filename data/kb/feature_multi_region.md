# Multi-Region Deployment Guide

**Document Type:** Feature
**Last Updated:** 2026-03-15
**Applies To:** Professional, Enterprise
**Tier:** Tier 1

## Summary

CloudOps Platform supports deploying clusters across multiple geographic regions, enabling high availability and lower-latency access for geographically distributed users. This guide covers supported regions, how to create multi-region deployments, and important limitations.

## Supported Regions

| Region Code | Location |
|---|---|
| us-east-1 | US East (Virginia) |
| us-west-2 | US West (Oregon) |
| eu-west-1 | Europe (Ireland) |
| eu-central-1 | Europe (Frankfurt) |
| ap-southeast-1 | Asia Pacific (Singapore) |
| ap-northeast-1 | Asia Pacific (Tokyo) |

Region availability may vary. Check current availability at [status.cloudops.example](https://status.cloudops.example).

## Multi-Region Architecture Patterns

CloudOps supports two multi-region patterns:

### Pattern 1 — Active-Active
Run the same workload in multiple regions simultaneously. Requires your application to support distributed state management.
- Use a global load balancer (not managed by CloudOps) to route traffic to the nearest healthy region.
- Each region has its own independent CloudOps cluster.

### Pattern 2 — Active-Passive (Disaster Recovery)
Run your primary workload in one region, with a standby cluster in a second region kept synchronized via backup/restore.
- Use CloudOps scheduled backups (see [feature_backup_scheduling.md](feature_backup_scheduling.md)) to replicate to the DR region.
- Failover is manual: restore the latest backup in the DR cluster and update your DNS/load balancer.

## Creating a Cluster in a Specific Region

```bash
cloudopsctl cluster create \
  --name my-eu-cluster \
  --region eu-west-1 \
  --kubernetes-version 1.29 \
  --node-pool-instance-type standard-4 \
  --node-count 3
```

Or in the Web Console: **Clusters > Create Cluster > Region** dropdown.

## Cross-Region Data Transfer

Data transferred between CloudOps clusters in different regions is billed as outbound data transfer. See [pricing_usage_billing.md](pricing_usage_billing.md).

## Limitations

- **Starter plan:** Single region only. Multi-region requires Professional or Enterprise.
- Cross-region cluster management (e.g., federating clusters) is not supported in v1.
- Each cluster in a multi-region setup is independent — there is no built-in cluster mesh.

## Related Documents
- [feature_auto_scaling.md](feature_auto_scaling.md)
- [feature_backup_scheduling.md](feature_backup_scheduling.md)
- [pricing_usage_billing.md](pricing_usage_billing.md)
