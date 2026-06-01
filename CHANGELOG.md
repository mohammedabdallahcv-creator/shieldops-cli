# Changelog

## v1.0.3 (2026-05-30)

### Changed
- README screenshots converted from SVG to PNG for reliable rendering

## v1.0.2 (2026-05-30)

### Added
- **Local Dockerfile analysis** — `shieldops analyze` works offline with 10+ built-in rules
- No API key required for basic analysis; key unlocks cloud AI analysis
- Added `--api` flag to force cloud analysis when logged in

### Changed
- Updated platform URL from `shieldops-ai.onrender.com` → `shieldops-ai.dev`

## v1.0.1 (2026-05-30)

### Changed
- Updated platform URL from `shieldops-ai.onrender.com` → `shieldops-ai.dev`

## v1.0.0 (2026-05-30)

### Initial Release

- **Dockerfile Security Scan** — Severity-graded analysis with CIS, SOC 2, NIST compliance mapping
- **AI-Powered Autofix** — Generate and apply fixes with `--apply` flag
- **Kubernetes Manifest Scan** — Scan deployment, pod, and service YAML files
- **Docker Compose Scan** — Scan docker-compose.yml for security misconfigurations
- **Docker Image Scan** — Scan container images for vulnerabilities
- **SBOM Generation** — Generate Software Bill of Materials from requirements.txt, package.json, Dockerfile
- **Compose Generation** — Generate docker-compose.yml from Dockerfile
- **Interactive TUI** — Slash-command interface with fuzzy completion and history
- **Multiple Output Formats** — table, JSON, SARIF, summary
- **CI/CD Integration** — `--fail-on` flag for pipeline gating
- **GitHub Actions & GitLab CI** — Ready-to-use workflow templates
- **Free Tier** — 5 scans/day with no credit card required
