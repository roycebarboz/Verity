# Acceptable Use Policy

**Document Type:** Policy
**Last Updated:** 2026-03-15
**Applies To:** All Plans
**Tier:** Tier 1

## Summary

This Acceptable Use Policy (AUP) governs what activities are and are not permitted on the CloudOps Platform. Violations may result in account suspension or termination without refund.

## Permitted Uses

CloudOps Platform may be used for:
- Running production, staging, and development Kubernetes workloads
- Hosting web applications, APIs, data pipelines, and machine learning workloads
- Testing and CI/CD workflows
- Any lawful commercial or personal software projects

## Prohibited Uses

The following activities are strictly prohibited on CloudOps Platform:

### Security Violations
- Unauthorized access attempts to other customers' clusters, infrastructure, or accounts
- Deploying malware, ransomware, spyware, or any malicious software
- Conducting network scanning, port scanning, or penetration testing without written approval
- Attempting to circumvent platform security controls

### Resource Abuse
- Cryptocurrency mining or blockchain proof-of-work computations
- Running workloads designed to consume excessive resources in a way that impacts other customers (noisy neighbor behavior)
- Deliberately triggering error conditions to exploit platform retry mechanisms

### Legal Violations
- Hosting or distributing child sexual abuse material (CSAM) — reported immediately to authorities
- Copyright infringement at scale
- Facilitating spam, phishing, or fraudulent activity
- Violating any applicable export control or sanctions regulations

### Platform Integrity
- Attempting to access CloudOps internal infrastructure or other customers' data
- Submitting manifests containing privileged containers intended to escape the node sandbox
- Attempting to exploit the CloudOps API beyond documented rate limits

## Container Security Policy

All containers deployed on CloudOps Platform must comply with:
- Non-root execution (`runAsNonRoot: true` in security context)
- No privileged containers (`privileged: false`)
- Resource requests and limits set on all containers (Professional and Enterprise plans)
- No host namespace sharing (`hostNetwork`, `hostPID`, `hostIPC` are prohibited)

Manifests violating these constraints are rejected with error CO-602.

## Enforcement

Violations of this policy may result in:
1. Immediate cluster suspension pending investigation
2. Permanent account termination without refund
3. Legal referral where required by law

## Reporting Violations

To report a suspected violation by another CloudOps customer, contact `security@cloudops.example`.

## Related Documents
- [policy_security_incident.md](policy_security_incident.md)
- [runbook_co602.md](runbook_co602.md)
- [escalation_legal_compliance.md](escalation_legal_compliance.md)
