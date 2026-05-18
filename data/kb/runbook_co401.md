# CO-401: Authentication Failure — Runbook

**Document Type:** Runbook
**Last Updated:** 2026-03-15
**Applies To:** All Plans
**Tier:** Tier 1

## Summary

Error CO-401 indicates an authentication failure. The CloudOps Platform rejected a request because the supplied credentials — API key, session token, or SSO assertion — were missing, invalid, or expired.

## Symptoms

- HTTP 401 response from `api.cloudops.example/v1`
- "Authentication failed" message in the Web Console at `console.cloudops.example`
- `cloudopsctl` returning: `Error: CO-401 — authentication failure`
- Users unable to log in via SSO

## Diagnostic Steps

### Step 1 — Identify the source

Determine where CO-401 is occurring:
- **Web Console login:** Likely a password, SSO, or MFA issue.
- **API call:** Likely an invalid or revoked API key.
- **CLI:** Likely a misconfigured or expired API key in the CLI config.

### Step 2 — Check API key validity

```bash
cloudopsctl config show
# Review the api_key field
cloudopsctl whoami
# If CO-401, the key is invalid or revoked
```

Navigate to [console.cloudops.example](https://console.cloudops.example) > **Settings > API > API Keys** and verify the key status is **Active**.

### Step 3 — Check for expired session

Web Console sessions expire after 24 hours of inactivity. Clear browser cookies and log in again.

### Step 4 — SSO-specific checks

- Verify the ACS URL in your IdP configuration matches the value in **Admin > Security > SSO**.
- Confirm the IdP metadata has not been rotated. Re-upload the metadata XML if needed.
- Check that the user's account is active in the IdP.

### Step 5 — MFA-related CO-401

If CO-401 appears after entering MFA code:
- Verify the time on the MFA device is synchronized (TOTP codes are time-sensitive, within ±30 seconds).
- Try a backup code. See [faq_two_factor_recovery.md](faq_two_factor_recovery.md).

## Resolution

| Root Cause | Resolution |
|---|---|
| Revoked API key | Generate a new API key. See [faq_api_key_rotation.md](faq_api_key_rotation.md). |
| Wrong password | Use the password reset flow. See [faq_password_reset.md](faq_password_reset.md). |
| Expired SSO assertion | Re-authenticate in the IdP, then return to CloudOps. |
| MFA time drift | Sync the clock on the authenticator device. |

## Escalation

If CO-401 persists after completing all steps above, escalate to Tier 2 with:
- The affected user's email
- Timestamp and method of the failing authentication
- Whether the issue affects all users or a specific user

## Related Documents
- [faq_password_reset.md](faq_password_reset.md)
- [faq_api_key_rotation.md](faq_api_key_rotation.md)
- [faq_sso_configuration.md](faq_sso_configuration.md)
