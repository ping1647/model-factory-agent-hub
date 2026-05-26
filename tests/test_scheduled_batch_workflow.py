from pathlib import Path

WORKFLOW_PATH = Path(".github/workflows/scheduled-batch-run.yml")
SCRIPT_PATH = Path("scripts/append_batch_health_log.py")
APPEND_TEST_PATH = Path("tests/test_append_batch_health_log.py")
WORKFLOW_TEST_PATH = Path("tests/test_scheduled_batch_workflow.py")

FILES_TO_SCAN = [WORKFLOW_PATH, SCRIPT_PATH, APPEND_TEST_PATH, WORKFLOW_TEST_PATH]

FORBIDDEN_BIDI = [
    "\u202a",
    "\u202b",
    "\u202c",
    "\u202d",
    "\u202e",
    "\u2066",
    "\u2067",
    "\u2068",
    "\u2069",
]


def test_file_line_counts_exceed_thresholds():
    assert len(WORKFLOW_PATH.read_text(encoding="utf-8").splitlines()) > 50
    assert len(SCRIPT_PATH.read_text(encoding="utf-8").splitlines()) > 80
    assert len(APPEND_TEST_PATH.read_text(encoding="utf-8").splitlines()) > 40
    assert len(WORKFLOW_TEST_PATH.read_text(encoding="utf-8").splitlines()) > 40


def test_workflow_contains_required_structure_and_commands():
    text = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert 'cron: "30 0 * * *"' in text
    assert "workflow_dispatch:" in text
    assert "PYTHONPATH: ." in text
    assert "id: tests" in text
    assert "id: batch" in text
    assert "continue-on-error: true" in text
    assert "if: ${{ always() }}" in text
    assert "--tests-status \"${{ steps.tests.outcome }}\"" in text
    assert "--batch-status \"${{ steps.batch.outcome }}\"" in text
    assert "Final failure gate" in text

    assert "data/runs" in text
    assert "data/dashboard/latest_dashboard_data.json" in text
    assert "app/dashboard/public/dashboard_data.json" in text
    assert "data/logs/batch_health_log.jsonl" in text


def test_new_files_have_no_forbidden_bidi_characters():
    for path in FILES_TO_SCAN:
        text = path.read_text(encoding="utf-8")
        for marker in FORBIDDEN_BIDI:
            assert marker not in text, f"Forbidden bidi character {marker!r} in {path}"
