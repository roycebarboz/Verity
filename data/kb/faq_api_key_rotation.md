# How Do I Rotate My API Key?

**Document Type:** FAQ
**Last Updated:** 2026-03-15
**Applies To:** All Plans
**Tier:** Tier 1

## Summary

API keys for the CloudOps REST API (`api.cloudops.example/v1`) should be rotated regularly as a security best practice. This article explains how to generate a new key and safely transition your integrations.

## Steps to Rotate Your API Key

1. Log in to [console.cloudops.example](https://console.cloudops.example).
2. Navigate to **Settings > API > API Keys**.
3. Click **Create New Key**.
4. Give the key a descriptive name (e.g., `prod-deploy-key-2026-03`).
5. Select the appropriate permission scope (read-only, read-write, or admin).
6. Click **Generate Key**. Copy the key immediately — it will not be displayed again.
7. Update your integrations (CI/CD pipelines, `cloudopsctl` config, application environment variables) with the new key.
8. Once confirmed working, return to **Settings > API > API Keys**, locate the old key, and click **Revoke**.

## CLI Configuration

After rotating, update your CLI config:
```bash
cloudopsctl config set-api-key YOUR_NEW_KEY
cloudopsctl whoami  # Verify the new key works
```

## Security Best Practices

- Never commit API keys to source control.
- Use separate keys for different environments (staging, production).
- Assign the minimum required scope for each key.
- Rotate keys at least every 90 days, or immediately after a suspected compromise.

## Error CO-401 After Rotation

If you receive a CO-401 after rotating, ensure the old key has not yet been revoked while the new key is still being propagated. Allow up to 60 seconds for key activation.

## Related Documents
- [runbook_co401.md](runbook_co401.md)
- [feature_iam_rbac.md](feature_iam_rbac.md)
- [faq_cli_installation.md](faq_cli_installation.md)
