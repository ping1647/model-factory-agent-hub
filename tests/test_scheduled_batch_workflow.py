from __future__ import annotations

from pathlib import Path


WORKFLOW_PATH = Path(".github/workflows/scheduled-batch-run.yml")
SCRIPT_PATH = Path("scripts/append_batch_health_log.py")
HEALTH_LOG_TEST_PATH = Path("tests/test_append_batch_health_log.py")
WORKFLOW_TEST_PATH = Path("tests/test_scheduled_batch_workflow.py")

BIDI_CONTROL_CHARS = {
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


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_scheduled_batch_workflow_is_multiline_and_structured():
    text = _read(WORKFLOW_PATH)

    assert len(text.splitlines()) > 50
    assert "name: Scheduled Batch Run" in text
    assert '    - cron: "30 0 * * *"' in text
    assert "\n  workflow_dispatch:\n" in text
    assert "\npermissions:\n  contents: write\n" in text
    assert "\nconcurrency:\n  group: scheduled-batch-run\n" in text
    assert "\njobs:\n  scheduled-batch-run:\n" in text
    assert "\n    runs-on: ubuntu-latest\n" in text
    assert "\n    env:\n      PYTHONPATH: .\n" in text
    assert "uses: actions/checkout@v4" in text
    assert "fetch-depth: 0" in text
    assert 'python-version: "3.11"' in text
    assert "run: python -m pip install pytest" in text


def test_scheduled_batch_workflow_logs_failures_before_failing_job():
    text = _read(WORKFLOW_PATH)

    assert "id: tests" in text
    assert "id: batch" in text
    assert text.count("continue-on-error: true") >= 2
    assert "run: pytest tests -q" in text
    assert "run: python scripts/run_manual_batch.py" in text
    assert "if: ${{ always() }}" in text
    assert "python scripts/append_batch_health_log.py" in text
    assert '--tests-status "${{ steps.tests.outcome }}"' in text
    assert '--batch-status "${{ steps.batch.outcome }}"' in text
    assert "data/logs/batch_health_log.jsonl" in text
    assert "data/dashboard/latest_dashboard_data.json" in text
    assert "app/dashboard/public/dashboard_data.json" in text
    assert "data/runs" in text
    assert "Fail if tests or batch failed" in text
    assert "steps.tests.outcome == 'failure'" in text
    assert "steps.batch.outcome == 'failure'" in text
    assert "exit 1" in text


def test_new_files_are_not_collapsed_and_have_no_bidi_control_chars():
    expected_min_lines = {
        WORKFLOW_PATH: 50,
        SCRIPT_PATH: 80,
        HEALTH_LOG_TEST_PATH: 40,
        WORKFLOW_TEST_PATH: 40,
    }

    for path, min_lines in expected_min_lines.items():
        text = _read(path)
        assert len(text.splitlines()) > min_lines, f"{path} appears collapsed"
        for char in BIDI_CONTROL_CHARS:
            assert char not in text, f"{path} contains forbidden bidi control character"
