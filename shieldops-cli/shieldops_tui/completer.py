"""Custom word completer for ShieldOps TUI slash commands."""
from __future__ import annotations

from prompt_toolkit.completion import CompleteEvent, Completer, Completion
from prompt_toolkit.document import Document

SLASH_COMMANDS = [
    "/analyze",
    "/analyze-json",
    "/autofix",
    "/sbom",
    "/compose-scan",
    "/compose-generate",
    "/k8s-scan",
    "/scan-image",
    "/login",
    "/logout",
    "/whoami",
    "/config",
    "/save",
    "/help",
    "/clear",
    "/exit",
]

COMMAND_DESCRIPTIONS = {
    "/analyze": "Analyze Dockerfile for security issues (local, free)",
    "/analyze-json": "Analyze Dockerfile, output JSON",
    "/autofix": "AI auto-fix for Dockerfile (cloud, requires API key)",
    "/sbom": "Generate Software Bill of Materials (cloud)",
    "/compose-scan": "Scan docker-compose.yml for issues (cloud)",
    "/compose-generate": "Generate docker-compose.yml from Dockerfile (cloud)",
    "/k8s-scan": "Scan Kubernetes manifest YAML (cloud)",
    "/scan-image": "Scan Docker image vulnerabilities (local, needs Trivy)",
    "/login": "Authenticate with API key",
    "/logout": "Remove stored credentials",
    "/whoami": "Show account info and plan",
    "/config": "View or change CLI settings",
    "/save": "Save last scan report to file",
    "/help": "Show available commands",
    "/clear": "Clear the screen",
    "/exit": "Exit the TUI",
}


class ShieldOpsCompleter(Completer):
    """Completer for slash commands and command arguments."""

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> list[Completion]:
        text = document.text_before_cursor.strip()

        if text.startswith("/"):
            parts = text.split(None, 1)
            cmd = parts[0]

            if len(parts) == 1:
                for full_cmd in SLASH_COMMANDS:
                    if full_cmd.startswith(cmd):
                        desc = COMMAND_DESCRIPTIONS.get(full_cmd, "")
                        yield Completion(
                            full_cmd,
                            start_position=-len(cmd),
                            display=full_cmd,
                            display_meta=desc,
                        )
