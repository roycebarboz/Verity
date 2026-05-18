# Browser Compatibility and Mobile Access

**Document Type:** FAQ
**Last Updated:** 2026-03-15
**Applies To:** All Plans
**Tier:** Tier 1

## Summary

The CloudOps Platform Web Console is designed for modern desktop browsers. This article details supported browsers, known limitations on mobile devices, and recommended alternatives for mobile workflows.

## Supported Desktop Browsers

| Browser | Minimum Version | Support Level |
|---|---|---|
| Google Chrome | 110+ | Full support (recommended) |
| Mozilla Firefox | 110+ | Full support |
| Microsoft Edge | 110+ | Full support |
| Apple Safari | 16+ | Full support |
| Opera | 95+ | Full support |
| Internet Explorer | Any | Not supported |

**Tip:** Always use the latest stable version of your browser for the best experience and security.

## Mobile Browser Support

The Web Console is accessible on mobile browsers, but is not optimized for small screens. The following limitations apply:

- Cluster topology diagrams may not render correctly on screens narrower than 768px.
- Some modal dialogs require horizontal scrolling.
- Drag-and-drop operations (e.g., node pool reordering) are not supported on touch devices.

**Recommended mobile approach:** Use the `cloudopsctl` CLI via a terminal app (e.g., Termux on Android, iSH on iOS) for cluster management tasks.

## Browser Extensions

Some browser extensions interfere with the console:

- **Ad blockers** may block console telemetry and cause blank dashboard panels.
- **Script blockers** can prevent the CLI download manager from functioning.
- **VPN extensions** may affect SSO redirect flows.

If you experience issues, try loading `console.cloudops.example` in a private/incognito window with extensions disabled.

## Related Documents
- [faq_console_url.md](faq_console_url.md)
- [faq_cli_installation.md](faq_cli_installation.md)
- [faq_sso_configuration.md](faq_sso_configuration.md)
