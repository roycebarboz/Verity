# CO-403: Permission Denied — Runbook

**Document Type:** Runbook
**Last Updated:** 2026-03-15
**Applies To:** All Plans
**Tier:** Tier 1

## Summary

Error CO-403 indicates a permission denied failure. The user is authenticated (identity confirmed) but does not have the authorization to perform the requested action. This is distinct from CO-401, which indicates the identity itself was not confirmed.

## Symptoms

- HTTP 403 response from `api.cloudops.example/v1`
- "You do not have permission to perform this action" message in the Web Console
- `cloudopsctl` returning: `Error: CO-403 — permission denied`
- Unable to access a specific cluster, delete a resource, or view billing information

## Diagnostic Steps

### Step 1 — Identify the action and role

Determine exactly what action failed and what role the user holds:

1. Navigate to [console.cloudops.example](https://console.cloudops.example) > **Settings > Team > Members**.
2. Find the affected user and note their current role.
3. Compare the role's permissions against the action they attempted using the table in [feature_iam_rbac.md](feature_iam_rbac.md).

### Step 2 — Check API key scope

If the failure is on an API call, verify the API key's permission scope:
- Navigate to **Settings > API > API Keys**.
- Confirm the key has the scope required for the action (read-only, read-write, or admin).

### Step 3 — Cluster-level RBAC

CloudOps supports cluster-level role assignments in addition to organization-level roles. A user may be an Operator at the organization level but only a Viewer on a specific cluster.

1. Navigate to **Clusters > [Cluster Name] > Settings > Access**.
2. Review the cluster-level role assignment for the affected user.

### Step 4 — Check for resource-level locks

Some resources can be locked to prevent modification. A locked cluster returns CO-403 for all write operations until unlocked by an Organization Admin.

## Resolution

| Root Cause | Resolution |
|---|---|
| Insufficient organization role | Upgrade the user's role. See [faq_adding_team_members.md](faq_adding_team_members.md). |
| API key scope too narrow | Generate a new key with the correct scope. See [faq_api_key_rotation.md](faq_api_key_rotation.md). |
| Cluster-level restriction | Add cluster-level access for the user in the cluster settings. |
| Resource lock | Unlock the resource as an Organization Admin. |

## Escalation

If the correct permissions are confirmed but CO-403 persists, escalate to Tier 2 with the exact API endpoint or console action that failed, the user's role, and the cluster ID.

## Related Documents
- [feature_iam_rbac.md](feature_iam_rbac.md)
- [faq_adding_team_members.md](faq_adding_team_members.md)
- [runbook_co401.md](runbook_co401.md)
