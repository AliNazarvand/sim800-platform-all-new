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
