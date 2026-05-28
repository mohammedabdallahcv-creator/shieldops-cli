# Security Policy

## Reporting a Vulnerability

If you believe you have found a security vulnerability in ShieldOps CLI or the ShieldOps AI platform, please report it responsibly.

**Do not** open a public GitHub issue for security vulnerabilities.

Please email: **security@shieldops.ai**

Include:
- A description of the vulnerability.
- Steps to reproduce.
- ShieldOps CLI version (`shieldops --version`).
- Python version and OS.

We will respond within 48 hours and work with you to resolve the issue.

## What We Consider a Security Issue

- Authentication bypass or token leakage
- Secret or API key exposure in logs or output
- Data sent to the backend being logged or stored improperly
- Command injection or arbitrary code execution
- Dependency vulnerabilities in pinned packages

## What Is NOT a Security Issue

- CLI output formatting issues
- Missing features or documentation gaps
- Performance issues (unless exploitable)
- Non-exploitable bugs (report via GitHub Issues instead)
