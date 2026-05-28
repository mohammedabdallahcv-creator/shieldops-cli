# ShieldOps CLI

> AI-powered security scanner for Dockerfiles, Kubernetes, Docker Compose, and more. Scan, fix, and secure your infrastructure from the terminal.

[![PyPI version](https://img.shields.io/badge/pypi-v1.0.0-blue.svg)](https://pypi.org/project/shieldops-cli/)
[![Python](https://img.shields.io/pypi/pyversions/shieldops-cli.svg)](https://pypi.org/project/shieldops-cli/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Powered by ShieldOps AI](https://img.shields.io/badge/powered%20by-ShieldOps%20AI-8B5CF6)](https://shieldops-ai.dev/)

---

## Why ShieldOps CLI

Most Dockerfile/K8s scanners tell you **what** is wrong. ShieldOps CLI also tells you **how to fix it** — using AI that understands your specific configuration, not generic rule text.

| Feature | ShieldOps CLI | Hadolint | Trivy |
|---|---|---|---|
| Dockerfile scan | Yes | Yes | Partial |
| Docker Compose scan | Yes | No | No |
| K8s manifest scan | Yes | No | Yes |
| AI-powered autofix | Yes | No | No |
| SBOM generation | Yes | No | Yes |
| Compose file generation | Yes | No | No |
| Docker image scan | Yes | No | Yes (built-in) |
| Interactive TUI | Yes | No | No |
| CI/CD ready (`--fail-on`) | Yes | Yes | Yes |
| Free tier | Yes (5 scans/day) | Yes | Yes |

### What makes it different

1. **AI Autofix** — not just "you have a problem" but "here's your fixed Dockerfile, ready to apply"
2. **Interactive TUI** — slash-command interface with fuzzy completion, history, and live spinner (think Claude Code but for security scans)
3. **One tool, many inputs** — Dockerfile, docker-compose.yml, K8s YAML, requirements.txt, package.json, Docker images
4. **CI/CD gate** — `--fail-on high` exits non-zero in pipelines so bad configs never merge

---

## Quick Start

```bash
# 1. Install
pip install shieldops-cli

# 2. Login (free tier — 5 scans/day)
shieldops login

# 3. Scan your Dockerfile
shieldops analyze Dockerfile
```

That's it. You get severity-graded findings, compliance mapping (CIS, SOC 2, NIST), and AI remediation guidance.

---

## Installation

### From PyPI

```bash
pip install shieldops-cli
```

### With TUI (interactive terminal)

```bash
pip install 'shieldops-cli[tui]'
```

### CI/CD (no TUI)

```bash
pip install shieldops-cli
```

---

## Commands

### `analyze` — Dockerfile Security Scan

```bash
shieldops analyze Dockerfile
shieldops analyze Dockerfile --format json
shieldops analyze Dockerfile --fail-on high        # CI/CD gate
shieldops analyze Dockerfile --open-report         # open browser report
```

### `autofix` — AI-Powered Dockerfile Fix

```bash
shieldops autofix Dockerfile                       # see suggested fix
shieldops autofix Dockerfile --apply               # apply fix in-place (.bak backup)
shieldops autofix Dockerfile --format json -o fix.json
```

### `sbom` — Software Bill of Materials

```bash
shieldops sbom requirements.txt
shieldops sbom package.json
shieldops sbom Dockerfile --format json
```

### `compose-scan` — Docker Compose Scan

```bash
shieldops compose-scan docker-compose.yml
shieldops compose-scan docker-compose.yml --fail-on high
```

### `compose-generate` — Generate Compose from Dockerfile

```bash
shieldops compose-generate Dockerfile
shieldops compose-generate Dockerfile --output docker-compose.yml
```

### `k8s-scan` — Kubernetes Manifest Scan

```bash
shieldops k8s-scan deployment.yaml
shieldops k8s-scan pod.yaml --format sarif
```

### `scan-image` — Docker Image Scan

```bash
shieldops scan-image nginx:latest
shieldops scan-image myapp:v1.2.3 --format json
```

### `login` / `logout` / `whoami`

```bash
shieldops login                     # interactive prompt
shieldops login --key sk-...        # direct key
export SHIELDOPS_API_KEY=sk-...     # or env var (CI/CD)
shieldops whoami
shieldops logout
```

---

## Output Formats

| Format | Best For |
|---|---|
| `table` (default) | Terminal reading |
| `json` | Scripting, API integration |
| `sarif` | GitHub Security tab, CodeQL |
| `summary` | One-line pipeline status |

```bash
shieldops analyze Dockerfile --format json --output scan.json
shieldops analyze Dockerfile --format sarif --output results.sarif
shieldops analyze Dockerfile --format summary
```

---

## TUI — Interactive Terminal Interface

```bash
shieldops tui
```

Slash-command interface with fuzzy completion, command history, and live loading spinner:

```
shieldops> /analyze
Path to Dockerfile: ./Dockerfile
Analyzing... [results]
Completed

shieldops> /autofix
Path to Dockerfile: ./Dockerfile
[AI fix suggestions]

shieldops> /save
Report saved: reports/autofix_20260528_143022.txt

shieldops> /exit
Session closed.
```

**Available commands**: `/analyze`, `/autofix`, `/sbom`, `/compose-scan`, `/compose-generate`, `/k8s-scan`, `/scan-image`, `/login`, `/logout`, `/whoami`, `/config`, `/save`, `/help`, `/clear`, `/exit`

Append `-json` to any scan command for JSON output (e.g., `/analyze-json`).

**Tab** = autocomplete, **Up/Down** = history, **/save** = write to file, **/exit** = return to normal terminal for scroll/copy.

---

## CI/CD Integration

### GitHub Actions

```yaml
name: ShieldOps Security Scan
on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install ShieldOps CLI
        run: pip install shieldops-cli
      - name: Scan Dockerfile
        env:
          SHIELDOPS_API_KEY: ${{ secrets.SHIELDOPS_API_KEY }}
        run: shieldops analyze Dockerfile --fail-on high --format sarif --output results.sarif
      - name: Upload SARIF
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: results.sarif
```

### GitLab CI

```yaml
shieldops-scan:
  image: python:3.11-slim
  stage: test
  before_script:
    - pip install shieldops-cli
  script:
    - shieldops analyze Dockerfile --fail-on high --format summary
  variables:
    SHIELDOPS_API_KEY: $SHIELDOPS_API_KEY
```

### Exit Codes

| Code | Meaning |
|---|---|
| `0` | Pass — no issues above threshold |
| `1` | Fail — issues found at or above `--fail-on` severity |
| `2` | Error — auth, network, or configuration problem |

---

## Free vs Pro

| Feature | Free | Pro |
|---|---|---|
| Scans per day | 5 | Unlimited |
| Dockerfile analysis | Yes | Yes |
| K8s / Compose scan | Yes | Yes |
| SBOM | Yes | Yes |
| AI Autofix | Yes | Yes + `--apply` |
| Image scan | Yes | Yes |
| HTML reports | Yes | Yes + PDF |
| Browser reports | Yes | Yes |
| Team access | No | Yes |
| Policy engine | No | Yes |
| Priority queue | No | Yes |

Get your API key at [https://shieldops-ai.dev/](https://shieldops-ai.dev/).

---

## Configuration

```bash
shieldops config list             # show all settings
shieldops config set api_url ...  # custom API endpoint
shieldops config get api_key      # check stored key
```

Config is stored in `~/.shieldops/config.json`. API keys are stored as-is (encrypt at rest on your machine if needed).

---

## What Runs Where

| Component | Runs Locally | Requires API Key |
|---|---|---|
| CLI argument parsing | Yes | No |
| File reading & validation | Yes | No |
| Output formatting (table/json/sarif) | Yes | No |
| Security analysis | No | Yes — sent to ShieldOps AI backend |
| AI autofix | No | Yes |
| SBOM generation | No | Yes |
| Report generation | No | Yes |

The CLI reads your file locally and sends only the file content (never secrets, env vars, or other system data) to the ShieldOps AI backend for analysis. Your file is not stored on our servers beyond the scan session.

---

## Development

```bash
git clone https://github.com/mohammedabdallahcv-creator/shieldops-cli.git
cd shieldops-cli
pip install -e '.[dev]'
pytest
```

Run the CLI from source:

```bash
python -m shieldops_cli.main analyze Dockerfile
```

---

## License

MIT

---

ShieldOps CLI is open-source. The analysis backend is proprietary and hosted at [shieldops-ai.onrender.com](https://shieldops-ai.dev/).
