from pathlib import Path


BIDI_CONTROL_CHARS = [
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

PR18_FILES = [
    ".github/workflows/scheduled-batch-run.yml",
    "scripts/append_batch_health_log.py",
    "tests/test_append_batch_health_log.py",
    "tests/test_scheduled_batch_workflow.py",
]


def test_scheduled_batch_workflow_multiline_structure() -> None:
    workflow_text = Path(".github/workflows/scheduled-batch-run.yml").read_text(encoding="utf-8")

    assert "\n  schedule:\n" in workflow_text
    assert "\n    - cron: \"30 0 * * *\"" in workflow_text
    assert "\n  workflow_dispatch:\n" in workflow_text
    assert "\n  scheduled-batch-run:\n" in workflow_text
    assert "\n    runs-on: ubuntu-latest\n" in workflow_text
    assert "\n    env:\n      PYTHONPATH: .\n" in workflow_text
    assert "\n    steps:\n" in workflow_text

    assert "run: pytest tests -q" in workflow_text
    assert "run: python scripts/run_manual_batch.py" in workflow_text
    assert (
        "run: python scripts/append_batch_health_log.py --tests-status passed --batch-status passed"
        in workflow_text
    )
    assert (
        "git add data/runs data/dashboard/latest_dashboard_data.json app/dashboard/public/dashboard_data.json data/logs/batch_health_log.jsonl"
        in workflow_text
    )


def test_pr18_files_have_no_bidi_chars_and_expected_line_counts() -> None:
    min_lines_by_file = {
        ".github/workflows/scheduled-batch-run.yml": 40,
        "scripts/append_batch_health_log.py": 50,
        "tests/test_append_batch_health_log.py": 20,
        "tests/test_scheduled_batch_workflow.py": 20,
    }

    for file_path in PR18_FILES:
        path = Path(file_path)
        text = path.read_text(encoding="utf-8")

        assert "\r" not in text, f"{file_path} contains CR characters"
        for control_char in BIDI_CONTROL_CHARS:
            assert control_char not in text, (
                f"{file_path} contains bidi control char U+{ord(control_char):04X}"
            )

        line_count = len(text.splitlines())
        assert line_count > min_lines_by_file[file_path], (
            f"{file_path} has too few lines ({line_count})"
        )
