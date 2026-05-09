"""SARIF v2.1.0 formatter for CI/CD integration."""
import json


def to_sarif(task: str, result: dict) -> str:
    findings = (
        result.get("report_contract", {}).get("detailed_issues")
        or result.get("results")
        or result.get("findings")
        or []
    )

    rules = {}
    sarif_results = []

    for f in findings:
        rule_id = f.get("rule_id") or f.get("canonical_rule_id") or f"shieldops-{len(rules)}"
        sev = str(f.get("severity", "info")).lower()
        sarif_level = {
            "critical": "error",
            "high": "error",
            "medium": "warning",
            "low": "note",
        }.get(sev, "note")

        if rule_id not in rules:
            rules[rule_id] = {
                "id": rule_id,
                "shortDescription": {"text": f.get("title") or f.get("message", rule_id)},
                "defaultConfiguration": {"level": sarif_level},
            }

        line = int(f.get("line") or 1)
        sarif_results.append({
            "ruleId": rule_id,
            "level": sarif_level,
            "message": {"text": f.get("message") or f.get("title", "")},
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {"uri": f.get("file", "Dockerfile")},
                    "region": {"startLine": line},
                }
            }],
        })

    sarif_doc = {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/sarif-2.1/schema/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {
                "driver": {
                    "name": "ShieldOps AI",
                    "informationUri": "https://shieldops-ai.onrender.com",
                    "version": "1.0.0",
                    "rules": list(rules.values()),
                }
            },
            "results": sarif_results,
        }],
    }

    return json.dumps(sarif_doc, indent=2, ensure_ascii=False)
