# How Do I Recover Access When I've Lost My Two-Factor Device?

**Document Type:** FAQ
**Last Updated:** 2026-03-15
**Applies To:** All Plans
**Tier:** Tier 1

## Summary

If you lose access to your MFA device (phone, hardware key, or authenticator app), you can recover account access using your backup codes or by contacting support. This article walks through both paths.

## Option 1 — Use a Backup Code

When you enabled MFA, you were given 10 single-use backup codes. To use one:

1. Navigate to [console.cloudops.example/login](https://console.cloudops.example/login).
2. Enter your email and password.
3. On the MFA screen, click **Use a backup code instead**.
4. Enter one of your saved backup codes.
5. Log in and immediately navigate to **Settings > Security** to re-enroll a new MFA device.

Backup codes are each valid for one use only. After all 10 are used, you must contact support.

## Option 2 — Contact Support

If you do not have backup codes, contact Tier 1 support:

1. Visit [support.cloudops.example](https://support.cloudops.example) and submit a ticket with the subject **MFA Recovery Request**.
2. Provide: your registered email, organization name, and the last 4 digits of the billing card on file.
3. A support agent will verify your identity and temporarily suspend MFA on your account.
4. Log in and re-enroll a new MFA device within 24 hours.

## Preventing Future Lockouts

- Store backup codes in a password manager or a secure physical location.
- Add SMS as a secondary MFA method as a fallback.
- For Enterprise accounts, ask your admin to configure account recovery via your IdP.

## Related Documents
- [faq_mfa_setup.md](faq_mfa_setup.md)
- [faq_password_reset.md](faq_password_reset.md)
- [escalation_tier2.md](escalation_tier2.md)
