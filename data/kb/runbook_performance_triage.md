# Performance Degradation Triage — Runbook

**Document Type:** Runbook
**Last Updated:** 2026-03-15
**Applies To:** All Plans
**Tier:** Tier 2

## Summary

This runbook covers the investigation and remediation of performance degradation in CloudOps clusters — including high latency, slow deployments, and elevated error rates — that do not constitute a full outage but are impacting production workloads.

## Symptoms

- API response times from `api.cloudops.example/v1` elevated but not returning 5xx
- Deployment rollouts taking significantly longer than baseline
- Workload pods responding slowly or intermittently failing health checks
- Customer-reported latency increases in applications hosted on CloudOps clusters
- Datadog or monitoring dashboards showing elevated P95 latency

## Phase 1 — Initial Triage (First 5 Minutes)

### Step 1 — Check platform status

Visit [status.cloudops.example](https://status.cloudops.example). If a platform degradation is listed, subscribe to updates. If not, the issue is likely cluster-specific.

### Step 2 — Gather baseline metrics

In the Web Console: **Clusters > [Cluster Name] > Metrics**

Collect current values for:
- CPU utilization per node
- Memory utilization per node
- Network I/O per node
- Pod restart counts in the last 30 minutes

### Step 3 — Identify the scope

Is the degradation affecting:
- **All nodes:** Likely a control plane or network issue
- **A specific node pool:** Likely resource saturation in that pool
- **Specific workloads:** Likely an application-level issue (out of CloudOps support scope)

## Phase 2 — Resource Exhaustion Investigation

```bash
cloudopsctl cluster metrics --cluster-id YOUR_CLUSTER_ID --interval 1h
```

Look for nodes approaching resource limits:
- CPU > 85%: Consider scaling up or adding nodes
- Memory > 80%: Check for memory leaks in workloads
- Disk I/O > 90%: Check for pods writing excessive logs or temporary files

### Scaling the Node Pool

If nodes are saturated, scale up the relevant node pool:
```bash
cloudopsctl nodepool scale --cluster-id YOUR_CLUSTER_ID \
  --pool-id POOL_ID --desired-count NEW_COUNT
```

## Phase 3 — Network Investigation

Intermittent latency often traces to network issues:
- Check for CO-502 errors on specific nodes (unreachable upstream)
- Verify DNS resolution within the cluster is functioning
- Check for network policy changes made in the last 24 hours via audit logs

## Escalation

Escalate to Tier 2 if:
- Resource utilization looks normal but performance is degraded
- The issue has lasted more than 30 minutes
- Customers are actively impacted and mitigation steps have not improved the situation

Provide: cluster ID, metrics output, audit log entries from the last 24 hours, and a description of the workloads affected.

## Related Documents
- [runbook_co502.md](runbook_co502.md)
- [runbook_node_pool_scaling.md](runbook_node_pool_scaling.md)
- [escalation_tier2.md](escalation_tier2.md)
