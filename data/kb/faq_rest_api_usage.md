# How Do I Use the CloudOps REST API?

**Document Type:** FAQ
**Last Updated:** 2026-03-15
**Applies To:** All Plans
**Tier:** Tier 1

## Summary

The CloudOps REST API (`api.cloudops.example/v1`) provides programmatic access to all platform features including cluster management, deployment triggers, and billing inquiries. This article covers authentication, base URL, and key usage patterns.

## Base URL

```
https://api.cloudops.example/v1
```

Interactive API documentation (OpenAPI/Swagger UI) is available at:
```
https://api.cloudops.example/v1/docs
```

## Authentication

All API requests require an `Authorization` header with your API key:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://api.cloudops.example/v1/clusters
```

If you receive **error CO-401**, your API key is missing, invalid, or expired. See [faq_api_key_rotation.md](faq_api_key_rotation.md).

## Rate Limits

| Plan | Requests per minute | Burst limit |
|---|---|---|
| Starter | 60 | 100 |
| Professional | 300 | 500 |
| Enterprise | 1,000 | 2,000 |

If you exceed the rate limit, the API returns **error CO-429** with a `Retry-After` header indicating when you can resume requests.

## Common Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/clusters` | List all clusters |
| POST | `/clusters` | Create a new cluster |
| GET | `/clusters/{id}` | Get cluster details |
| DELETE | `/clusters/{id}` | Delete a cluster |
| POST | `/clusters/{id}/deploy` | Deploy a manifest |

## Error Handling

API errors follow a standard format:
```json
{
  "error_code": "CO-429",
  "message": "Rate limit exceeded",
  "retry_after": 30
}
```

## Related Documents
- [faq_api_key_rotation.md](faq_api_key_rotation.md)
- [runbook_co429.md](runbook_co429.md)
- [runbook_co401.md](runbook_co401.md)
