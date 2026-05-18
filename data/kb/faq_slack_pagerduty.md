# How Do I Configure Slack and PagerDuty Integrations?

**Document Type:** FAQ
**Last Updated:** 2026-03-15
**Applies To:** Professional, Enterprise
**Tier:** Tier 1

## Summary

CloudOps Platform integrates with Slack and PagerDuty to deliver real-time alerts for cluster events, deployment completions, and error conditions. This article covers setup for both integrations.

## Slack Integration

### Prerequisites
- You must have a Slack workspace and the ability to install apps.
- You must be a CloudOps Organization Admin.

### Setup Steps

1. Navigate to [console.cloudops.example](https://console.cloudops.example) > **Settings > Integrations > Slack**.
2. Click **Connect Slack**.
3. Authorize the CloudOps app in the Slack OAuth flow.
4. Select one or more Slack channels to receive notifications.
5. Configure which event types trigger notifications (cluster errors, deployment success, billing alerts, etc.).
6. Click **Save Configuration**.

### Alert Types Sent to Slack

- Cluster health alerts (CO-500, CO-502, CO-503, CO-504)
- Deployment success/failure notifications
- Billing payment failures (CO-701)
- Node scaling events

## PagerDuty Integration

### Prerequisites
- A PagerDuty account with a service configured.
- PagerDuty Integration Key (found in your PagerDuty service settings under **Integrations > Add an Integration > Events API v2**).

### Setup Steps

1. Navigate to **Settings > Integrations > PagerDuty**.
2. Paste your PagerDuty **Integration Key**.
3. Set the minimum severity threshold for PagerDuty alerts (recommended: P1/P2 only).
4. Click **Save and Test**. A test incident will be created in PagerDuty.

## Related Documents
- [runbook_co500.md](runbook_co500.md)
- [escalation_outage_communication.md](escalation_outage_communication.md)
- [feature_iam_rbac.md](feature_iam_rbac.md)
