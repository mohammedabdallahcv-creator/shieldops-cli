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
