# How Do I Add Team Members to My Organization?

**Document Type:** FAQ
**Last Updated:** 2026-03-15
**Applies To:** All Plans
**Tier:** Tier 1

## Summary

Organization Admins can invite new team members to CloudOps Platform from the Web Console. This article covers inviting users, setting roles, and managing seat limits by plan.

## Steps to Add a Team Member

1. Log in to [console.cloudops.example](https://console.cloudops.example) as an **Organization Admin**.
2. Navigate to **Settings > Team > Members**.
3. Click **Invite Member**.
4. Enter the team member's email address.
5. Select a role from the dropdown (see Roles section below).
6. Click **Send Invitation**.

The invitee will receive an email from `noreply@cloudops.example` with a link to accept the invitation and create their account. The invitation link expires after **72 hours**.

## Roles

| Role | Cluster Access | Billing Access | Admin Settings |
|---|---|---|---|
| Viewer | Read-only | None | None |
| Developer | Read + Deploy | None | None |
| Operator | Full cluster access | None | None |
| Billing Admin | None | Full | None |
| Organization Admin | Full | Full | Full |

## Seat Limits

- **Starter ($99/mo):** Up to 5 team members
- **Professional ($499/mo):** Up to 25 team members
- **Enterprise:** Unlimited

If you have reached your seat limit, you must upgrade your plan or remove an existing member before sending new invitations.

## Removing a Member

Navigate to **Settings > Team > Members**, click the three-dot menu next to the member's name, and select **Remove from Organization**. Their access is revoked immediately.

## Related Documents
- [faq_transfer_ownership.md](faq_transfer_ownership.md)
- [feature_iam_rbac.md](feature_iam_rbac.md)
- [pricing_plan_comparison.md](pricing_plan_comparison.md)
