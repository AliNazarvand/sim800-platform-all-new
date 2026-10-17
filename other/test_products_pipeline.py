import json
from pathlib import Path


def test_products_have_expected_scale_and_provenance():
    root = Path(__file__).resolve().parents[2]
    commands = [json.loads(line) for line in (root / "dataset/commands.jsonl").read_text().splitlines() if line]
    errors = [json.loads(line) for line in (root / "dataset/error_codes.jsonl").read_text().splitlines() if line]
    deprecated = [json.loads(line) for line in (root / "dataset/deprecated_commands.jsonl").read_text().splitlines() if line]
    assert len(commands) >= 50
    assert len(errors) >= 50
    assert len(deprecated) >= 1
    assert all(item["source"] for item in commands)
    assert {item["category"] for item in errors} == {"CME", "CMS"}
    assert all(item["compared_versions"] for item in deprecated)
