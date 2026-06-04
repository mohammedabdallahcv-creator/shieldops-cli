"""Output formatters for ShieldOps CLI."""
from shieldops_cli import config


def format_result(task: str, result: dict, fmt: str | None = None) -> str:
    fmt = fmt or config.get("default_format", "table")
    if fmt == "json":
        from shieldops_cli.formatters.json_fmt import to_json
        return to_json(result)
    if fmt == "sarif":
        from shieldops_cli.formatters.sarif import to_sarif
        return to_sarif(task, result)
    if fmt == "summary":
        from shieldops_cli.formatters.summary import to_summary
        return to_summary(task, result)
    from shieldops_cli.formatters.table import to_table
    return to_table(task, result)
