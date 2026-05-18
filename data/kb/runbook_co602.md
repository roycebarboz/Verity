# CO-602: Invalid Manifest — Runbook

**Document Type:** Runbook
**Last Updated:** 2026-03-15
**Applies To:** All Plans
**Tier:** Tier 1

## Summary

Error CO-602 indicates that a Kubernetes manifest submitted for deployment failed validation. The manifest may contain invalid YAML syntax, unknown API versions, missing required fields, or values that violate CloudOps Platform policy constraints.

## Symptoms

- HTTP 400 response with `error_code: CO-602` when deploying via API or CLI
- "Invalid manifest" error in the Web Console deployment interface
- `cloudopsctl deploy` returning: `Error: CO-602 — invalid manifest: [specific error message]`

## Common Causes

| Cause | Example Error Message |
|---|---|
| Invalid YAML syntax | `yaml: mapping values are not allowed in this context` |
| Unknown API version | `no matches for kind "Deployment" in version "apps/v2"` |
| Missing required field | `spec.selector is required` |
| Container image not specified | `spec.containers[0].image is required` |
| Policy violation | `containers must not run as root (UID 0)` |
| Resource limits not set | `resource limits required on all containers (Professional+)` |

## Diagnostic Steps

### Step 1 — Read the full error message

The CO-602 response body includes a detailed validation error message. Always read it completely before troubleshooting. Example:

```json
{
  "error_code": "CO-602",
  "message": "Invalid manifest",
  "details": [
    "spec.containers[0].resources.limits is required",
    "spec.containers[0].securityContext.runAsNonRoot must be true"
  ]
}
```

### Step 2 — Validate locally before submitting

Use `kubectl` to validate manifests locally before submission:

```bash
kubectl apply --dry-run=client -f your-manifest.yaml
```

Or validate against the CloudOps API schema:
```bash
cloudopsctl manifest validate --file your-manifest.yaml
```

### Step 3 — Check for policy constraints

CloudOps enforces additional security policies on top of standard Kubernetes validation. Review [policy_acceptable_use.md](policy_acceptable_use.md) for the full list.

Common enforced constraints:
- Containers must run as non-root
- Resource requests and limits must be set on all containers (Professional and Enterprise)
- Privileged containers are not allowed

## Resolution

Fix the errors listed in the CO-602 response body, then resubmit. After fixing syntax errors, run `cloudopsctl manifest validate` before deploying.

## Escalation

CO-602 should not require escalation — it is always a client-side validation error. If you believe a valid manifest is being incorrectly rejected, contact Tier 2 support with the manifest content and the exact CO-602 response body.

## Related Documents
- [policy_acceptable_use.md](policy_acceptable_use.md)
- [feature_auto_scaling.md](feature_auto_scaling.md)
- [runbook_cluster_wont_start.md](runbook_cluster_wont_start.md)
