"""JSON output formatter."""
import json


def to_json(result: dict) -> str:
    return json.dumps(result, indent=2, ensure_ascii=False, default=str)
