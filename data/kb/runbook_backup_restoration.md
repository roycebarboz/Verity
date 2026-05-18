# Backup Restoration Procedure — Runbook

**Document Type:** Runbook
**Last Updated:** 2026-03-15
**Applies To:** Professional, Enterprise
**Tier:** Tier 2

## Summary

This runbook covers the procedure for restoring a cluster from a scheduled or on-demand backup. Backup restoration is available on Professional and Enterprise plans. It replaces the cluster state with a point-in-time snapshot of persistent volumes and configuration.

## Prerequisites

- Backup restoration is available on **Professional ($499/mo)** and **Enterprise** plans only.
- You must have **Operator** or **Organization Admin** role.
- A backup must exist for the target cluster. See [feature_backup_scheduling.md](feature_backup_scheduling.md) to verify scheduled backups are enabled.

## Step 1 — Identify the Backup to Restore

List available backups for your cluster:
```bash
cloudopsctl backup list --cluster-id YOUR_CLUSTER_ID
```

This returns a list with backup IDs, timestamps, and status. Identify the `backup_id` of the point-in-time you want to restore.

Or in the Web Console: **Clusters > [Cluster Name] > Backups**.

## Step 2 — Verify Backup Integrity

Before restoring, verify the backup is complete and uncorrupted:
```bash
cloudopsctl backup verify --backup-id BACKUP_ID
```

A `status: healthy` response confirms the backup is restorable. A `status: corrupted` or `status: incomplete` backup cannot be used — choose the next oldest healthy backup.

## Step 3 — Initiate Restoration

> ⚠️ **Warning:** Restoration replaces the current cluster state with the backup snapshot. All changes made after the backup timestamp will be lost. Workloads on the cluster will be unavailable during restoration (typically 5–15 minutes).

```bash
cloudopsctl backup restore --backup-id BACKUP_ID --cluster-id YOUR_CLUSTER_ID --confirm
```

Or in the Web Console: **Clusters > [Cluster Name] > Backups > [Backup] > Restore**.

## Step 4 — Monitor the Restoration

```bash
cloudopsctl operation status --operation-id RESTORE_OPERATION_ID
```

The restoration completes when the cluster status returns to `RUNNING` and the operation status shows `COMPLETE`.

## Step 5 — Post-Restore Verification

After restoration completes:
1. Verify workloads are running: `cloudopsctl cluster nodes list --cluster-id YOUR_CLUSTER_ID`
2. Confirm application health by checking your application's health endpoints.
3. Review audit logs for the restoration event: **Admin > Audit Logs**.

## Escalation

If restoration fails or the cluster does not return to `RUNNING` within 30 minutes, escalate to Tier 3 (Engineering) immediately. Data recovery situations are P1 — use the emergency escalation path in [escalation_engineering.md](escalation_engineering.md).

## Related Documents
- [feature_backup_scheduling.md](feature_backup_scheduling.md)
- [escalation_engineering.md](escalation_engineering.md)
- [runbook_cluster_wont_start.md](runbook_cluster_wont_start.md)
