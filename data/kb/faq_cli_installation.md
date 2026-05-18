# How Do I Install the CloudOps CLI?

**Document Type:** FAQ
**Last Updated:** 2026-03-15
**Applies To:** All Plans
**Tier:** Tier 1

## Summary

The `cloudopsctl` command-line tool allows you to manage clusters, deploy workloads, and interact with the CloudOps API from your terminal. This article covers installation on macOS, Linux, and Windows.

## Installation

### macOS

```bash
brew tap cloudops/tap
brew install cloudopsctl
```

### Linux (x86_64)

```bash
curl -sSL https://downloads.cloudops.example/cli/latest/linux-amd64/cloudopsctl -o /usr/local/bin/cloudopsctl
chmod +x /usr/local/bin/cloudopsctl
```

### Windows (PowerShell)

```powershell
Invoke-WebRequest -Uri "https://downloads.cloudops.example/cli/latest/windows-amd64/cloudopsctl.exe" -OutFile "$env:LOCALAPPDATA\cloudopsctl\cloudopsctl.exe"
# Add the directory to your PATH
```

## Initial Setup

After installation, authenticate with your API key:

```bash
cloudopsctl config set-api-key YOUR_API_KEY
cloudopsctl whoami
```

You should see your account name and plan tier. If you see error CO-401, verify your API key is correct and has not been revoked.

## Verifying the Installation

```bash
cloudopsctl version
# Expected output: cloudopsctl v2.x.x (linux/amd64)
```

## Updating the CLI

macOS: `brew upgrade cloudopsctl`
Linux/Windows: Re-run the installation command above. The installer always fetches the latest version.

## Related Documents
- [faq_api_key_rotation.md](faq_api_key_rotation.md)
- [runbook_co401.md](runbook_co401.md)
- [feature_iam_rbac.md](feature_iam_rbac.md)
