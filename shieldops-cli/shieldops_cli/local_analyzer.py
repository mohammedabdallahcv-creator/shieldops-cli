#!/usr/bin/env python3
"""
ShieldOps CLI — Local Dockerfile Analyzer
Performs security analysis of Dockerfile content locally (no cloud credits).
Used for free-tier users to avoid consuming API quota on simple Dockerfile scans.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List


# ── Severity levels ────────────────────────────────────────────────────
CRITICAL = "critical"
HIGH = "high"
MEDIUM = "medium"
LOW = "low"
INFO = "info"

# ── Rules: (pattern, rule_id, title, severity, fix) ──────────────────
RULES: List[Dict[str, Any]] = [
    {
        "id": "DS001",
        "title": "Latest tag used",
        "severity": HIGH,
        "pattern": r"^FROM\s+\S+:latest\b",
        "fix": "Pin specific image version (e.g., python:3.12-slim)",
    },
    {
        "id": "DS002",
        "title": "No tag specified (defaults to :latest)",
        "severity": MEDIUM,
        "pattern": r"^FROM\s+(\S+)(?!\:)(?!\s+AS\s)",
        "fix": "Add explicit version tag",
    },
    {
        "id": "DS003",
        "title": "Running as root (no USER directive)",
        "severity": HIGH,
        "check": "no_user",
        "fix": "Add 'USER <non-root-user>' before CMD/ENTRYPOINT",
    },
    {
        "id": "DS004",
        "title": "ADD used instead of COPY",
        "severity": LOW,
        "pattern": r"^ADD\s+",
        "fix": "Use COPY instead of ADD unless you need remote URL extraction",
    },
    {
        "id": "DS005",
        "title": "Curl/wget piped to shell",
        "severity": CRITICAL,
        "pattern": r"(curl|wget)\s+[^\|]*\|\s*(bash|sh)\b",
        "fix": "Download to file first, verify checksum, then run",
    },
    {
        "id": "DS006",
        "title": "apt-get update without install in same RUN",
        "severity": MEDIUM,
        "pattern": r"^RUN\s+apt-get\s+update\s*$",
        "fix": "Combine 'apt-get update' with 'apt-get install' in single RUN",
    },
    {
        "id": "DS007",
        "title": "No apt-get clean after install",
        "severity": LOW,
        "check": "apt_clean",
        "fix": "Add '&& rm -rf /var/lib/apt/lists/*' after install",
    },
    {
        "id": "DS008",
        "title": "Exposed SSH port",
        "severity": CRITICAL,
        "pattern": r"^EXPOSE\s+22\b",
        "fix": "Remove SSH exposure from container image",
    },
    {
        "id": "DS009",
        "title": "Privileged port < 1024",
        "severity": INFO,
        "pattern": r"^EXPOSE\s+([1-9]|[1-9][0-9]|[1-9][0-9]{2})\b",
        "fix": "Use unprivileged port (>= 1024) to avoid requiring root",
    },
    {
        "id": "DS010",
        "title": "COPY with --chown runs as root",
        "severity": LOW,
        "check": "chown_safe",
        "fix": "Pre-create user and use '--chown=user:group'",
    },
    {
        "id": "DS011",
        "title": "Secrets in ENV/ARG",
        "severity": CRITICAL,
        "check": "secrets",
        "fix": "Use Docker secrets or runtime env vars, never bake into image",
    },
    {
        "id": "DS012",
        "title": "Using sudo in container",
        "severity": HIGH,
        "pattern": r"(sudo\s+|/usr/bin/sudo)",
        "fix": "Remove sudo, run as non-root user instead",
    },
    {
        "id": "DS013",
        "title": "HEALTHCHECK missing",
        "severity": LOW,
        "check": "no_healthcheck",
        "fix": "Add HEALTHCHECK directive for production containers",
    },
    {
        "id": "DS014",
        "title": "MAINTAINER deprecated",
        "severity": INFO,
        "pattern": r"^MAINTAINER\s+",
        "fix": "Use LABEL maintainer= instead",
    },
    {
        "id": "DS015",
        "title": "pip install without --no-cache-dir",
        "severity": LOW,
        "pattern": r"pip\s+install(?![^&|;]*--no-cache-dir)",
        "fix": "Add '--no-cache-dir' to keep image small",
    },
    {
        "id": "DS016",
        "title": "npm install without --production or ci",
        "severity": MEDIUM,
        "pattern": r"npm\s+install(?![^&|;]*(--production|--only=prod|--ci))",
        "fix": "Use 'npm ci --production' for reproducible builds",
    },
    {
        "id": "DS017",
        "title": "No WORKDIR set",
        "severity": INFO,
        "check": "no_workdir",
        "fix": "Set WORKDIR instead of using 'cd' in RUN commands",
    },
    {
        "id": "DS018",
        "title": "chmod 777 used",
        "severity": HIGH,
        "pattern": r"chmod\s+777",
        "fix": "Use minimal permissions (e.g., 755, 644)",
    },
    {
        "id": "DS019",
        "title": "Insecure HTTP URL in curl",
        "severity": MEDIUM,
        "pattern": r"(curl|wget)\s+['\"]?http://",
        "fix": "Use HTTPS instead of HTTP for downloads",
    },
    {
        "id": "DS020",
        "title": "Multiple RUNs can be combined",
        "severity": INFO,
        "check": "run_consolidation",
        "fix": "Combine consecutive RUN commands with && to reduce layers",
    },
]


def _line_for(content: str, match_start: int) -> int:
    return content[:match_start].count("\n") + 1


def analyze_dockerfile_local(content: str, filename: str = "Dockerfile") -> Dict[str, Any]:
    """Run local Dockerfile analysis. Returns dict compatible with cloud API format."""
    issues: List[Dict[str, Any]] = []
    has_user = bool(re.search(r"^USER\s+", content, re.MULTILINE))
    has_healthcheck = bool(re.search(r"^HEALTHCHECK\s+", content, re.MULTILINE))
    has_workdir = bool(re.search(r"^WORKDIR\s+", content, re.MULTILINE))
    has_apt_clean = "rm -rf /var/lib/apt/lists" in content
    has_chown = re.search(r"COPY\s+--chown=", content, re.MULTILINE)
    run_count = len(re.findall(r"^RUN\s+", content, re.MULTILINE))

    # Secret patterns
    secret_patterns = [
        (r"(?i)(password|passwd|pwd|secret|api[_-]?key|token|aws_access|private[_-]?key)\s*=\s*['\"]?[A-Za-z0-9+/=_\-]{8,}", "Hardcoded secret"),
        (r"AKIA[0-9A-Z]{16}", "AWS Access Key"),
        (r"-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----", "Private key"),
    ]

    for rule in RULES:
        if "pattern" in rule:
            matches = re.finditer(rule["pattern"], content, re.MULTILINE)
            for m in matches:
                issues.append({
                    "rule_id": rule["id"],
                    "title": rule["title"],
                    "severity": rule["severity"],
                    "fix": rule.get("fix", ""),
                    "line": _line_for(content, m.start()),
                    "line_end": _line_for(content, m.end()),
                    "evidence": m.group(0)[:200],
                    "confidence": 0.9,
                    "auto_fixable": False,
                })

        if rule.get("check") == "no_user" and not has_user and re.search(r"^(CMD|ENTRYPOINT)\s+", content, re.MULTILINE):
            issues.append({
                "rule_id": rule["id"],
                "title": rule["title"],
                "severity": rule["severity"],
                "fix": rule["fix"],
                "line": 1,
                "confidence": 0.95,
                "auto_fixable": False,
            })

        if rule.get("check") == "apt_clean" and re.search(r"apt-get\s+install", content) and not has_apt_clean:
            m = re.search(r"apt-get\s+install", content)
            issues.append({
                "rule_id": rule["id"],
                "title": rule["title"],
                "severity": rule["severity"],
                "fix": rule["fix"],
                "line": _line_for(content, m.start()) if m else 1,
                "confidence": 0.7,
                "auto_fixable": True,
            })

        if rule.get("check") == "chown_safe" and re.search(r"COPY\s+(?!--chown=)", content, re.MULTILINE) and not has_chown:
            m = re.search(r"COPY\s+(?!--chown=)", content, re.MULTILINE)
            issues.append({
                "rule_id": rule["id"],
                "title": rule["title"],
                "severity": rule["severity"],
                "fix": rule["fix"],
                "line": _line_for(content, m.start()) if m else 1,
                "confidence": 0.6,
                "auto_fixable": False,
            })

        if rule.get("check") == "secrets":
            for pat, name in secret_patterns:
                m = re.search(pat, content)
                if m:
                    issues.append({
                        "rule_id": rule["id"],
                        "title": f"{rule['title']}: {name}",
                        "severity": CRITICAL,
                        "fix": rule["fix"],
                        "line": _line_for(content, m.start()),
                        "evidence": m.group(0)[:50] + "...",
                        "confidence": 0.99,
                        "auto_fixable": False,
                    })

        if rule.get("check") == "no_healthcheck" and not has_healthcheck and re.search(r"^(CMD|ENTRYPOINT)\s+", content, re.MULTILINE):
            issues.append({
                "rule_id": rule["id"],
                "title": rule["title"],
                "severity": rule["severity"],
                "fix": rule["fix"],
                "line": 1,
                "confidence": 0.5,
                "auto_fixable": False,
            })

        if rule.get("check") == "no_workdir" and not has_workdir and re.search(r"^RUN\s+cd\s+", content, re.MULTILINE):
            issues.append({
                "rule_id": rule["id"],
                "title": rule["title"],
                "severity": rule["severity"],
                "fix": rule["fix"],
                "line": 1,
                "confidence": 0.7,
                "auto_fixable": False,
            })

        if rule.get("check") == "run_consolidation" and run_count >= 4:
            issues.append({
                "rule_id": rule["id"],
                "title": f"{rule['title']} ({run_count} RUN commands found)",
                "severity": rule["severity"],
                "fix": rule["fix"],
                "line": 1,
                "confidence": 0.5,
                "auto_fixable": True,
            })

    # Stats
    severity_counts = {CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0, INFO: 0}
    for issue in issues:
        sev = issue.get("severity", INFO)
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

    risk_score = (
        severity_counts[CRITICAL] * 25
        + severity_counts[HIGH] * 10
        + severity_counts[MEDIUM] * 4
        + severity_counts[LOW] * 1
    )
    risk_score = min(risk_score, 100)

    return {
        "ok": True,
        "engine": "shieldops-local",
        "powered_by": "ShieldOps CLI (local)",
        "plan": "free",
        "filename": filename,
        "issues": issues,
        "summary": {
            "total_issues": len(issues),
            "critical": severity_counts[CRITICAL],
            "high": severity_counts[HIGH],
            "medium": severity_counts[MEDIUM],
            "low": severity_counts[LOW],
            "info": severity_counts[INFO],
            "risk_score": risk_score,
        },
        "stats": severity_counts,
        "report_origin": "cli-local",
        "limits": {
            "is_local": True,
            "reason": "Free plan — Dockerfile analysis run locally to preserve cloud credits",
        },
    }


if __name__ == "__main__":
    import sys
    from pathlib import Path

    if len(sys.argv) < 2:
        print("Usage: python local_analyzer.py <Dockerfile>")
        sys.exit(1)

    dockerfile_path = Path(sys.argv[1])
    if not dockerfile_path.exists():
        print(f"File not found: {dockerfile_path}")
        sys.exit(1)

    content = dockerfile_path.read_text(encoding="utf-8")
    result = analyze_dockerfile_local(content, dockerfile_path.name)

    print(f"📄 {result['filename']}")
    print(f"🔧 {result['powered_by']}")
    print(f"📊 Risk score: {result['summary']['risk_score']}/100")
    print(f"   Critical: {result['summary']['critical']}, High: {result['summary']['high']}, Medium: {result['summary']['medium']}, Low: {result['summary']['low']}, Info: {result['summary']['info']}")
    print()
    for issue in result["issues"]:
        print(f"[{issue['severity'].upper():8}] Line {issue.get('line', '?'):4} {issue['rule_id']} — {issue['title']}")
        if issue.get("fix"):
            print(f"           💡 {issue['fix']}")


# Backwards-compat alias (used by analyze.py)
analyze_dockerfile = analyze_dockerfile_local
