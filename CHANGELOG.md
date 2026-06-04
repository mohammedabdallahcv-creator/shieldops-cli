# Changelog

## v1.0.5 (2026-06-05)

### Fixed
- Added missing README.md to package so PyPI shows project description properly

## v1.0.4 (2026-06-05)

### Added
- **Cyber-minimal TUI banner** — branded splash frame with ShieldOps ASCII wordmark
- **Cloud analysis in TUI** — `/analyze` and `/analyze-json` now use cloud AI when API key is present
- Server error passthrough in `whoami()` — shows actual error from server instead of generic message

### Fixed
- API keys URL corrected from `/settings/api-keys` to `/api-keys` across all CLI code and error messages

### Added
- **Interactive TUI** — `shieldops tui` launches a REPL with slash commands, tab completion, and history
- `/analyze` runs locally with 20 security rules — free users get real findings, no API key needed
- `/analyze-json` for JSON output, `/save` to persist reports, `/help` for command reference
- Cloud commands (`/autofix`, `/sbom`, `/compose-scan`, `/k8s-scan`) require API key via `/login`
- Formatters now support local analyzer output (`issues` key, `stats` severity counts)

### Changed
- Version bumped to 1.0.4

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
