from pathlib import Path

WORKFLOW_PATH = Path(".github/workflows/scheduled-batch-run.yml")
FILES_TO_SCAN = [
    Path(".github/workflows/scheduled-batch-run.yml"),
    Path("scripts/append_batch_health_log.py"),
    Path("tests/test_append_batch_health_log.py"),
    Path("tests/test_scheduled_batch_workflow.py"),
]
FORBIDDEN_BIDI = {
    "\u202a",
    "\u202b",
    "\u202c",
    "\u202d",
    "\u202e",
    "\u2066",
    "\u2067",
    "\u2068",
    "\u2069",
}


def test_workflow_has_expected_structure_and_commands():
    text = WORKFLOW_PATH.read_text(encoding="utf-8")
    lines = text.splitlines()

    assert len(lines) > 40
    assert 'cron: "30 0 * * *"' in text
    assert "workflow_dispatch:" in text
    assert "PYTHONPATH: ." in text
    assert "pytest tests -q" in text
    assert "python scripts/run_manual_batch.py" in text
    assert "python scripts/append_batch_health_log.py" in text
    assert "git add \\" in text
    assert "  schedule:" in text
    assert "    - cron:" in text


def test_all_new_files_are_multiline_and_have_no_bidi_characters():
    for path in FILES_TO_SCAN:
        text = path.read_text(encoding="utf-8")
        line_count = len(text.splitlines())
        assert line_count > 20, f"{path} appears collapsed with too few lines"

        for bidi in FORBIDDEN_BIDI:
            assert bidi not in text, f"Found forbidden bidi character {bidi!r} in {path}"
