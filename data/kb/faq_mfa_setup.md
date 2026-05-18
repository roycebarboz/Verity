# How Do I Set Up Multi-Factor Authentication?

**Document Type:** FAQ
**Last Updated:** 2026-03-15
**Applies To:** All Plans
**Tier:** Tier 1

## Summary

Multi-Factor Authentication (MFA) adds a second verification step to your CloudOps login, significantly reducing the risk of unauthorized access. This article covers enabling MFA via an authenticator app.

## Enabling MFA

1. Log in to [console.cloudops.example](https://console.cloudops.example).
2. Click your profile avatar (top-right corner) and select **Security Settings**.
3. Under **Multi-Factor Authentication**, click **Enable MFA**.
4. Choose **Authenticator App** (recommended) or **SMS**.
5. **Authenticator App flow:**
   - Scan the QR code displayed on screen using an app such as Google Authenticator, Authy, or 1Password.
   - Enter the 6-digit code shown in the app to confirm pairing.
   - Store the 10 backup codes that are displayed — these are shown only once.
6. Click **Confirm and Enable**. MFA will be required on your next login.

## MFA Methods Supported

| Method | Security Level | Recommended |
|---|---|---|
| Authenticator App (TOTP) | High | ✅ Yes |
| SMS One-Time Password | Medium | For backup only |
| Hardware Security Key (FIDO2) | Highest | Enterprise plan only |

## Important Notes

- **Enterprise plan** customers can enforce MFA organization-wide from the Admin Console.
- If you lose access to your MFA device, follow the recovery steps in [faq_two_factor_recovery.md](faq_two_factor_recovery.md).
- MFA settings are per-user, not per-organization (except when enforced by an admin).

## Related Documents
- [faq_password_reset.md](faq_password_reset.md)
- [faq_two_factor_recovery.md](faq_two_factor_recovery.md)
- [faq_sso_configuration.md](faq_sso_configuration.md)
