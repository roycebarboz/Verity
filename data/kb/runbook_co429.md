# CO-429: Rate Limit Exceeded — Runbook

**Document Type:** Runbook
**Last Updated:** 2026-03-15
**Applies To:** All Plans
**Tier:** Tier 1

## Summary

Error CO-429 is returned when a client has exceeded the CloudOps API rate limit for their subscription plan. All API requests after the limit is reached are rejected until the rate limit window resets.

## Symptoms

- HTTP 429 response from `api.cloudops.example/v1` with a `Retry-After` header
- `cloudopsctl` returning: `Error: CO-429 — rate limit exceeded. Retry after Xs`
- Automated CI/CD pipelines failing mid-run with 429 errors
- Slack notifications flooding about API failures

## Rate Limits by Plan

| Plan | Requests per minute | Burst limit |
|---|---|---|
| Starter ($99/mo) | 60 | 100 |
| Professional ($499/mo) | 300 | 500 |
| Enterprise (custom) | 1,000 | 2,000 |

## Diagnostic Steps

### Step 1 — Check the Retry-After header

When CO-429 is returned, the response includes a `Retry-After` header with the number of seconds to wait:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 30
Content-Type: application/json

{"error_code":"CO-429","message":"Rate limit exceeded","retry_after":30}
```

### Step 2 — Identify the source of excess requests

High request volume usually comes from:
- CI/CD pipelines running parallel deployments
- Monitoring scripts polling cluster status too frequently
- Misconfigured automation with no backoff logic

Review your API usage in the Web Console: **Admin > API Usage > Rate Limit History**.

### Step 3 — Check if multiple API keys share the limit

Rate limits are applied **per API key**. If multiple services share one key, they share the limit. Consider using separate keys per service.

## Resolution

1. **Immediate:** Honor the `Retry-After` value and implement exponential backoff in your code.
2. **Short-term:** Reduce polling frequency. Use webhooks instead of polling where possible.
3. **Long-term:** Upgrade your plan for a higher rate limit. See [pricing_plan_comparison.md](pricing_plan_comparison.md).

### Implementing Exponential Backoff (Python Example)

```python
import time
import requests

def api_call_with_backoff(url, headers, max_retries=3):
    for attempt in range(max_retries):
        response = requests.get(url, headers=headers)
        if response.status_code == 429:
            wait = int(response.headers.get("Retry-After", 30)) * (2 ** attempt)
            time.sleep(wait)
        else:
            return response
    raise Exception("Max retries exceeded")
```

## Escalation

If your workload legitimately requires more than your plan's rate limit and upgrading is not immediately feasible, contact support to request a temporary rate limit increase. Include your account ID, API key (last 4 characters), and estimated required rate.

## Related Documents
- [pricing_plan_comparison.md](pricing_plan_comparison.md)
- [faq_api_key_rotation.md](faq_api_key_rotation.md)
- [faq_rest_api_usage.md](faq_rest_api_usage.md)
