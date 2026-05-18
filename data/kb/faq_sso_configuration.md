# How Do I Configure SSO (Single Sign-On)?

**Document Type:** FAQ
**Last Updated:** 2026-03-15
**Applies To:** Professional, Enterprise
**Tier:** Tier 2

## Summary

CloudOps Platform supports SAML 2.0 and OIDC-based Single Sign-On (SSO), allowing your team to authenticate using your existing identity provider (IdP). SSO configuration is available on Professional and Enterprise plans.

## Supported Identity Providers

- Okta
- Microsoft Entra ID (formerly Azure AD)
- Google Workspace
- Any SAML 2.0 or OIDC-compliant provider

## Configuration Steps (SAML 2.0)

1. Log in as an **Organization Admin** at [console.cloudops.example](https://console.cloudops.example).
2. Navigate to **Admin > Security > Single Sign-On**.
3. Click **Configure SAML** and note the **ACS URL** and **Entity ID** — you will need these in your IdP.
4. In your identity provider, create a new SAML application using the ACS URL and Entity ID provided.
5. Copy the IdP **Metadata URL** or download the **Metadata XML** from your identity provider.
6. Paste the Metadata URL (or upload the XML) into the CloudOps SSO configuration form.
7. Click **Test Connection** — a test login window will open. Complete authentication through your IdP.
8. If the test succeeds, click **Enable SSO**.

## Provisioning and Deprovisioning

SCIM 2.0 provisioning is supported on Enterprise plans. With SCIM enabled, users added or removed in your IdP are automatically synced to CloudOps.

## Troubleshooting SSO

- **Error CO-401 during SSO login:** Verify the ACS URL in your IdP matches exactly, including trailing slash.
- **Users land on CloudOps login page instead of IdP:** Ensure the SSO domain is correctly configured under **Admin > Security > Verified Domains**.
- **Cannot access SSO settings:** You must have the **Organization Admin** role. Contact your admin to elevate your permissions.

## Related Documents
- [faq_mfa_setup.md](faq_mfa_setup.md)
- [faq_adding_team_members.md](faq_adding_team_members.md)
- [policy_acceptable_use.md](policy_acceptable_use.md)
