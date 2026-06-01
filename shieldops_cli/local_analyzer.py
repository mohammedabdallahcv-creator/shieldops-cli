"""Local Dockerfile analyzer — works offline, no API key needed."""
from __future__ import annotations
import re
from pathlib import Path

RULES: list[dict] = [
    # ── DL3007: latest tag ──
    {
        "rule_id": "DL3007",
        "severity": "critical",
        "pattern": re.compile(r"^FROM\s+\S+?:\s*latest\s*$", re.IGNORECASE | re.MULTILINE),
        "message": "Using `latest` tag is dangerous — pinned versions ensure reproducible builds",
        "fix": "Replace `latest` with a specific version tag (e.g. `python:3.11-slim`)",
        "category": "best_practice",
    },
    # ── DL3008: pin apt-get versions ──
    {
        "rule_id": "DL3008",
        "severity": "critical",
        "pattern": re.compile(
            r"RUN\s+(apt-get\s+install\s+)(?!.*\s=\s)",
            re.IGNORECASE | re.MULTILINE,
        ),
        "message": "Pin package versions in `apt-get install` for reproducible builds",
        "fix": "Add `=version` to each package (e.g. `build-essential=12.9`)",
        "category": "best_practice",
    },
    # ── DL3009: apt-get lists not cleaned ──
    {
        "rule_id": "DL3009",
        "severity": "medium",
        "pattern": re.compile(
            r"RUN\s+apt-get\s+install",
            re.IGNORECASE,
        ),
        "message": "Delete apt-get lists after install to reduce image size",
        "fix": "Add `&& rm -rf /var/lib/apt/lists/*` after apt-get install",
        "category": "best_practice",
        "_needs_clean": True,
    },
    # ── DL3013: pin pip versions ──
    {
        "rule_id": "DL3013",
        "severity": "high",
        "pattern": re.compile(
            r"RUN\s+pip\s+install\s+(?!.*==)",
            re.IGNORECASE | re.MULTILINE,
        ),
        "message": "Pin package versions in pip install for reproducible builds",
        "fix": "Use `pip install flask==3.0.0` instead of `pip install flask`",
        "category": "best_practice",
    },
    # ── DL4006: SHELL selected by default ──
    {
        "rule_id": "DL4006",
        "severity": "high",
        "pattern": re.compile(r"^SHELL\s+\[", re.IGNORECASE | re.MULTILINE),
        "message": "SHELL is already selected by default — remove redundant SHELL directive",
        "fix": "Remove the SHELL directive unless you need a non-default shell",
        "category": "style",
    },
    # ── DL4001: Windows line endings ──
    {
        "rule_id": "DL4001",
        "severity": "low",
        "pattern": re.compile(r"\r\n"),
        "message": "Windows-style line endings detected — use LF for Dockerfiles",
        "fix": "Convert to Unix line endings (LF)",
        "category": "style",
    },
    # ── DL3003: no WORKDIR before COPY ──
    {
        "rule_id": "DL3003",
        "severity": "low",
        "pattern": re.compile(r"^COPY\s+\.\s+/"),
        "message": "COPY without prior WORKDIR — files may land in unexpected location",
        "fix": "Add `WORKDIR /app` before COPY",
        "category": "best_practice",
    },
    # ── USER root ──
    {
        "rule_id": "SC1001",
        "severity": "critical",
        "pattern": re.compile(r"^USER\s+root\b", re.IGNORECASE | re.MULTILINE),
        "message": "Running as root increases blast radius in case of container escape",
        "fix": "Use `USER nonroot` or create a dedicated user with `RUN adduser -D appuser && USER appuser`",
        "category": "security",
    },
    # ── EXPOSE without port number ──
    {
        "rule_id": "DL4000",
        "severity": "low",
        "pattern": re.compile(r"^EXPOSE\s*$", re.MULTILINE),
        "message": "EXPOSE without port number has no effect",
        "fix": "Specify a port: `EXPOSE 8080`",
        "category": "best_practice",
    },
    # ── ENV with debug mode in production ──
    {
        "rule_id": "SC1002",
        "severity": "medium",
        "pattern": re.compile(
            r"ENV\s+(FLASK_DEBUG|NODE_ENV|DJANGO_DEBUG|APP_DEBUG)\s*=\s*(1|true|development)\b",
            re.IGNORECASE | re.MULTILINE,
        ),
        "message": "Debug/development mode enabled in production image",
        "fix": "Set `ENV FLASK_DEBUG=0` or remove the ENV line for production images",
        "category": "security",
    },
    # ── No HEALTHCHECK ──
    {
        "rule_id": "DL4002",
        "severity": "low",
        "pattern": re.compile(r"^(?!.*HEALTHCHECK)", re.MULTILINE),
        "message": "No HEALTHCHECK defined — container health won't be monitored",
        "fix": "Add `HEALTHCHECK CMD curl -f http://localhost:8080/health || exit 1`",
        "category": "best_practice",
        "_negate": True,
    },
    # ── RUN npm install without cache cleanup ──
    {
        "rule_id": "DL3014",
        "severity": "medium",
        "pattern": re.compile(
            r"RUN\s+npm\s+install\s+(?!.*npm\s+cache\s+clean)",
            re.IGNORECASE | re.MULTILINE,
        ),
        "message": "npm install without cache cleanup increases image size",
        "fix": "Add `&& npm cache clean --force` to the RUN command",
        "category": "best_practice",
    },
]

FINDING_TEMPLATE = {
    "type": "dockerfile",
    "category": "",
    "severity": "info",
    "rule_id": "",
    "message": "",
    "fix": "",
    "line": 1,
    "column": 1,
    "source": "shieldops-local",
}


def analyze_dockerfile(content: str, filename: str = "Dockerfile") -> dict:
    lines = content.split("\n")
    findings = []

    for rule in RULES:
        pattern = rule["pattern"]
        negate = rule.get("_negate", False)

        if negate:
            if not pattern.search(content):
                finding = dict(FINDING_TEMPLATE)
                finding.update(
                    severity=rule["severity"],
                    rule_id=rule["rule_id"],
                    message=rule["message"],
                    fix=rule["fix"],
                    category=rule["category"],
                    line=1,
                )
                findings.append(finding)
            continue

        for match in pattern.finditer(content):
            line_num = content[: match.start()].count("\n") + 1
            raw_line = lines[line_num - 1] if line_num <= len(lines) else ""

            if rule.get("_needs_clean"):
                block = content[match.start() : min(match.start() + 300, len(content))]
                if "rm -rf" in block and "apt/lists" in block:
                    continue

            if rule["rule_id"] == "DL3013":
                rest_of_line = raw_line[match.end() - len(raw_line) :]
                if "==" in rest_of_line or "requirements.txt" in rest_of_line or "-r" in rest_of_line:
                    continue

            if rule["rule_id"] == "DL3008":
                rest = raw_line[match.end() - len(raw_line) :]
                if "=" in rest:
                    continue

            finding = dict(FINDING_TEMPLATE)
            finding.update(
                severity=rule["severity"],
                rule_id=rule["rule_id"],
                message=rule["message"],
                fix=rule["fix"],
                category=rule["category"],
                line=line_num,
            )
            findings.append(finding)

    critical = sum(1 for f in findings if f["severity"] == "critical")
    high = sum(1 for f in findings if f["severity"] == "high")
    medium = sum(1 for f in findings if f["severity"] == "medium")
    low = sum(1 for f in findings if f["severity"] == "low")

    score = max(0, 100 - (critical * 25 + high * 10 + medium * 5 + low * 2))

    return {
        "findings": findings,
        "report_contract": {
            "critical_count": critical,
            "high_count": high,
            "medium_count": medium,
            "low_count": low,
        },
        "security_score": score,
        "security_score_grade": "A" if score >= 90 else "B" if score >= 70 else "C" if score >= 50 else "D" if score >= 30 else "F",
        "source": "local",
        "filename": filename,
    }
