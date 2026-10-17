import json
from pathlib import Path

from sim800_diffing import diff_commands
from sim800_validation import validate_jsonl


def test_validate_jsonl(tmp_path: Path):
    schema = tmp_path / "s.json"
    data = tmp_path / "d.jsonl"
    schema.write_text(
        json.dumps({"type": "object", "required": ["command"], "properties": {"command": {"type": "string"}}})
    )
    data.write_text('{"command":"AT"}\n{"bad":1}\n')
    report = validate_jsonl(data, schema)
    assert report["valid"] == 1 and report["invalid"] == 1


def test_diff_commands(tmp_path: Path):
    old, new = tmp_path / "old.jsonl", tmp_path / "new.jsonl"
    old.write_text('{"command":"AT+A"}\n')
    new.write_text('{"command":"AT+B"}\n')
    result = diff_commands(old, new)
    assert result == {"added": ["AT+B"], "removed": ["AT+A"], "changed": []}


def test_diff_detects_changed_record(tmp_path: Path):
    old, new = tmp_path / "old.jsonl", tmp_path / "new.jsonl"
    old.write_text('{"command":"AT+A","x":1}\n')
    new.write_text('{"command":"AT+A","x":2}\n')
    assert diff_commands(old, new)["changed"] == ["AT+A"]


def test_validation_writes_quarantine(tmp_path: Path):
    schema = tmp_path / "s.json"
    data = tmp_path / "d.jsonl"
    quarantine = tmp_path / "q.jsonl"
    schema.write_text(json.dumps({"type": "object", "required": ["command"]}))
    data.write_text('{"bad":1}\n')
    report = validate_jsonl(data, schema, quarantine)
    assert report["invalid"] == 1 and quarantine.exists()
