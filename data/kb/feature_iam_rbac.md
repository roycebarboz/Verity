# IAM and RBAC Overview

**Document Type:** Feature
**Last Updated:** 2026-03-15
**Applies To:** All Plans
**Tier:** Tier 1

## Summary

CloudOps Platform uses a role-based access control (RBAC) model to govern what users can do within an organization and within individual clusters. This guide explains the role hierarchy, how to assign roles, and how cluster-level permissions interact with organization-level roles.

## Organization-Level Roles

Every user in a CloudOps organization has exactly one organization-level role:

| Role | Description |
|---|---|
| **Viewer** | Read-only access to clusters and platform state. Cannot deploy, scale, or modify resources. |
| **Developer** | Can view and deploy to clusters. Cannot create or delete clusters. |
| **Operator** | Full cluster management access (create, delete, scale, deploy). No billing or admin access. |
| **Billing Admin** | Access to all billing and invoice features only. No cluster access. |
| **Organization Admin** | Full access to all features except organization deletion and ownership transfer. |
| **Organization Owner** | All permissions including ownership transfer and organization deletion. |

## Cluster-Level Role Overrides

In addition to the organization role, you can assign cluster-specific roles that override the organization role for a particular cluster:

- A user who is **Viewer** at the org level can be given **Operator** access on a specific cluster.
- A user who is **Operator** at the org level can be restricted to **Viewer** on a sensitive production cluster.

To set a cluster-level role:
1. Navigate to **Clusters > [Cluster Name] > Settings > Access**.
2. Click **Add Member Access**.
3. Select the user and their cluster-level role.

## API Key Scopes

API keys have independent permission scopes, separate from user roles:

| Scope | Permissions |
|---|---|
| `read` | GET operations only |
| `read-write` | GET + POST + PUT + PATCH |
| `admin` | All operations including DELETE |

Always use the minimum required scope for your API key.

## SCIM Provisioning (Enterprise)

Enterprise accounts with SCIM enabled can automatically sync user provisioning and role assignments from your identity provider. Group membership in the IdP maps to CloudOps organization roles via the SCIM role mapping configuration in **Admin > Security > SCIM**.

## Least Privilege Best Practices

- Assign **Developer** rather than **Operator** for users who only need to deploy workloads.
- Use **Billing Admin** for finance team members — they should not have cluster access.
- Rotate API keys quarterly and use one key per integration, not a shared key.
- Review organization membership quarterly and remove users who have left.

## Related Documents
- [faq_adding_team_members.md](faq_adding_team_members.md)
- [faq_api_key_rotation.md](faq_api_key_rotation.md)
- [faq_sso_configuration.md](faq_sso_configuration.md)
