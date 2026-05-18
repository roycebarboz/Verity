# Backup Scheduling — Feature Guide

**Document Type:** Feature
**Last Updated:** 2026-03-15
**Applies To:** Professional, Enterprise
**Tier:** Tier 1

## Summary

CloudOps Platform provides automated backup scheduling for cluster persistent volumes and configurations. This guide explains how to configure backup schedules, verify backup health, and understand retention policies.

## Availability

- **Starter ($99/mo):** Backups not available. Customers must export configurations manually.
- **Professional ($499/mo):** Automated backups included with 14-day retention.
- **Enterprise:** Automated backups with configurable retention up to 365 days.

## Enabling Backup Scheduling

### Via the Web Console

1. Log in to [console.cloudops.example](https://console.cloudops.example).
2. Navigate to **Clusters > [Cluster Name] > Backups**.
3. Click **Configure Backup Schedule**.
4. Set:
   - **Frequency:** Daily (default), every 6 hours, every 12 hours, or weekly
   - **Time:** UTC time to run the backup (default: 2:00 AM UTC)
   - **Retention:** Days to retain each backup (Professional default: 14 days)
5. Click **Save Schedule**.

### Via the CLI

```bash
cloudopsctl backup schedule set \
  --cluster-id YOUR_CLUSTER_ID \
  --frequency daily \
  --time 02:00 \
  --retention-days 14
```

## Creating On-Demand Backups

```bash
cloudopsctl backup create --cluster-id YOUR_CLUSTER_ID
```

On-demand backups count against your retention limit and storage quota like scheduled backups.

## Verifying Backup Health

To verify that recent backups are healthy:
```bash
cloudopsctl backup list --cluster-id YOUR_CLUSTER_ID --limit 5
```

Check the `status` field of each backup. Healthy backups show `status: healthy`. Investigate any backup with `status: incomplete` or `status: corrupted`.

Set up backup failure alerts in **Settings > Billing > Billing Alerts** — under **Backup Alerts**, enable **Notify on backup failure**.

## What Is Backed Up

Each backup includes:
- Kubernetes object manifests (Deployments, Services, ConfigMaps, Secrets)
- Persistent Volume (PV) data snapshots
- Node pool configuration

**Not included in backups:**
- In-memory state of running containers
- External databases not managed by CloudOps

## Restoring From a Backup

See [runbook_backup_restoration.md](runbook_backup_restoration.md) for the full restoration procedure.

## Related Documents
- [runbook_backup_restoration.md](runbook_backup_restoration.md)
- [policy_data_retention.md](policy_data_retention.md)
- [feature_multi_region.md](feature_multi_region.md)
