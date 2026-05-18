# Security Incident Disclosure Policy

**Document Type:** Policy
**Last Updated:** 2026-03-15
**Applies To:** All Plans
**Tier:** Tier 2

## Summary

This document describes how CloudOps Inc. identifies, responds to, and discloses security incidents that may affect customer data or platform integrity.

## What Constitutes a Security Incident

A security incident is any event that results in or has the potential to result in:
- Unauthorized access to customer data or cluster configurations
- Compromise of CloudOps Platform infrastructure
- Exposure of customer credentials or API keys
- A vulnerability exploited in the platform

## Incident Response Process

### Phase 1 — Detection and Triage
CloudOps Security team identifies and validates the incident. An incident severity rating is assigned:
- **P1:** Active breach with confirmed data exposure
- **P2:** Vulnerability exploited but no confirmed data exposure
- **P3:** Vulnerability discovered, not yet exploited

### Phase 2 — Containment
The Security team isolates affected systems, revokes compromised credentials, and prevents further exposure.

### Phase 3 — Investigation
Root cause analysis is performed. Scope of affected customers and data is determined.

### Phase 4 — Notification
- **P1 incidents:** Affected customers are notified within **72 hours** of confirmation, per GDPR Article 33 requirements.
- **P2 incidents:** Customers are notified within **7 days**.
- **P3 incidents:** Disclosed in release notes or security advisories within **30 days**.

Notification is sent to the Organization Owner's registered email.

## Vulnerability Disclosure (Responsible Disclosure)

CloudOps maintains a responsible disclosure program. If you discover a security vulnerability in the CloudOps Platform:

1. Do **not** publicly disclose until CloudOps has had the opportunity to remediate.
2. Report to `security@cloudops.example` with a description of the vulnerability and steps to reproduce.
3. CloudOps will acknowledge receipt within 2 business days and provide a remediation timeline.
4. After patching, CloudOps will credit the reporter in the security advisory (with permission).

## Customer Responsibilities

Customers are responsible for:
- Securing their own API keys (rotation, scope, storage)
- Configuring cluster access controls appropriately
- Reporting suspected unauthorized access to their clusters promptly

## Related Documents
- [policy_acceptable_use.md](policy_acceptable_use.md)
- [policy_privacy_summary.md](policy_privacy_summary.md)
- [escalation_legal_compliance.md](escalation_legal_compliance.md)
