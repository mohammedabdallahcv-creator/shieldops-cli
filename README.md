# ShieldOps CLI

> Security scanner CLI for Docker, Kubernetes, Compose, SBOM, and more.

## Installation

```bash
pip install shieldops-cli
```

Or from source:

```bash
pip install -e ./shieldops-cli
```

## Quick Start

```bash
# Authenticate
shieldops login --key sk-shieldops-pro_YOUR_KEY

# Or via environment variable (CI/CD)
export SHIELDOPS_API_KEY=sk-shieldops-pro_YOUR_KEY

# Scan a Dockerfile
shieldops analyze Dockerfile

# Scan Kubernetes manifest
shieldops k8s-scan deployment.yaml

# Scan Docker Compose
shieldops compose-scan docker-compose.yml

# Generate SBOM
shieldops sbom Dockerfile

# AutoFix
shieldops autofix Dockerfile

# Generate Compose
shieldops compose-generate Dockerfile

# Scan Docker image (requires Trivy)
shieldops scan-image nginx:latest
```

## Output Formats

```bash
shieldops analyze Dockerfile                          # Table (default)
shieldops analyze Dockerfile --format json            # JSON
shieldops analyze Dockerfile --format sarif           # SARIF (CI/CD)
shieldops analyze Dockerfile --format summary         # One-line summary
shieldops analyze Dockerfile -f json -o report.json   # Save to file
```

## TUI — Interactive Terminal Interface

Launch the full-screen TUI with slash commands, fuzzy completion, and command history:

```bash
shieldops tui
```

### TUI Commands

| Command | Description |
|---|---|
| `/analyze`, `/analyze-json` | Dockerfile scan |
| `/autofix`, `/autofix-json` | AI Dockerfile auto-fix |
| `/sbom`, `/sbom-json` | SBOM generation |
| `/compose-scan`, `/compose-scan-json` | Docker Compose scan |
| `/compose-generate`, `/compose-generate-json` | Compose file generation |
| `/k8s-scan`, `/k8s-scan-json` | Kubernetes manifest scan |
| `/scan-image`, `/scan-image-json` | Docker image scan |
| `/login` | Authenticate (hidden input) |
| `/logout` | Clear credentials |
| `/whoami` | Show login status |
| `/config`, `/config-set`, `/config-get` | Configuration |
| `/save [filename]` | Save last output to `reports/` directory |
| `/help` | List all commands |
| `/clear` | Clear screen |
| `/exit` | Exit TUI (results remain visible in terminal) |

### TUI Tips

- **Tab completion**: Type `/ana` + `Tab` to complete to `/analyze`
- **History**: Use `Up/Down` arrows to navigate previous commands
- **Saving results**: Use `/save` to write the last output to a file, or `/save custom.txt` for a specific filename
- **Copying results**: Use `/exit` to return to the normal terminal where standard scroll and select work
- **Loading indicator**: Long-running commands show an animated spinner during execution

## CI/CD Integration

### GitHub Actions

```yaml
name: ShieldOps Security Scan
on: [push, pull_request]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install ShieldOps CLI
        run: pip install shieldops-cli
      - name: Scan Dockerfile
        env:
          SHIELDOPS_API_KEY: ${{ secrets.SHIELDOPS_API_KEY }}
        run: shieldops analyze Dockerfile --fail-on high --format summary
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

## Configuration

```bash
shieldops config list                        # Show all settings
shieldops config set default_format json     # Change default format
shieldops config set api_url https://...     # Custom API URL
shieldops whoami                             # Show account info
```

## License

MIT
