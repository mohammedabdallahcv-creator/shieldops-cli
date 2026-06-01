# Contributing

Thanks for your interest in ShieldOps CLI.

## Getting Started

```bash
git clone https://github.com/mohammedabdallahcv-creator/shieldops-cli.git
cd shieldops-cli
pip install -e '.[dev,tui]'
pytest
```

## Reporting Issues

- Include ShieldOps CLI version (`shieldops --version`).
- Include Python version and OS.
- Include the command you ran and the full output.
- For security issues, see [SECURITY.md](SECURITY.md).

## Pull Requests

1. Fork the repo and create a branch from `main`.
2. Run `pytest` to make sure existing tests pass.
3. Add tests for new functionality.
4. Keep changes minimal and focused.
5. Update the README if commands or options changed.

## Code Style

- Match existing formatting (4-space indent, double quotes).
- No trailing whitespace.
- Type hints on new functions.
- Docstrings on public functions.

## Releasing

Maintainers handle releases. To request a release, open an issue tagged `release`.
