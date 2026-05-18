# What Is the CloudOps Console URL?

**Document Type:** FAQ
**Last Updated:** 2026-03-15
**Applies To:** All Plans
**Tier:** Tier 1

## Summary

The CloudOps Platform Web Console is accessible at a single URL for all customers. This article covers the console URL, supported browsers, and troubleshooting access issues.

## Console URL

**[https://console.cloudops.example](https://console.cloudops.example)**

Bookmark this URL. There are no tenant-specific subdomains for standard accounts. Enterprise accounts with custom SAML SSO may have a dedicated login portal — check with your Organization Admin.

## Supported Browsers

| Browser | Minimum Version | Notes |
|---|---|---|
| Google Chrome | 110+ | Fully supported and recommended |
| Mozilla Firefox | 110+ | Fully supported |
| Microsoft Edge | 110+ | Fully supported |
| Safari | 16+ | Supported; minor UI differences may apply |
| Opera | 95+ | Supported |

**Mobile browsers:** The Web Console is readable on mobile browsers but is not optimized for small screens. We recommend using the `cloudopsctl` CLI for mobile/tablet workflows.

## Troubleshooting Access

- **Page not loading:** Check [status.cloudops.example](https://status.cloudops.example) for any active incidents.
- **Redirected to login after logging in:** Clear cookies for `console.cloudops.example` and try again.
- **Error CO-401 at login:** Verify your credentials. If using SSO, confirm your IdP session is active.
- **Console loads but shows blank page:** Disable browser extensions (especially ad blockers or script blockers) and reload.

## Related Documents
- [faq_browser_compatibility.md](faq_browser_compatibility.md)
- [faq_sso_configuration.md](faq_sso_configuration.md)
- [runbook_co503.md](runbook_co503.md)
