from pathlib import Path


BIDI_CONTROLS = [
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

TARGET_FILES = [
    ".github/workflows/scheduled-batch-run.yml",
    "scripts/append_batch_health_log.py",
    "tests/test_append_batch_health_log.py",
    "tests/test_scheduled_batch_workflow.py",
]


def test_scheduled_batch_workflow_contains_expected_configuration() -> None:
    workflow_text = Path(".github/workflows/scheduled-batch-run.yml").read_text(encoding="utf-8")

    # Baseline content checks.
    assert "workflow_dispatch" in workflow_text
    assert "schedule" in workflow_text
    assert "30 0 * * *" in workflow_text
    assert "pytest tests -q" in workflow_text
    assert "python scripts/run_manual_batch.py" in workflow_text
    assert "PYTHONPATH: ." in workflow_text
    assert "scripts/append_batch_health_log.py" in workflow_text
    assert "data/logs/batch_health_log.jsonl" in workflow_text
    assert (
        "git add data/runs data/dashboard/latest_dashboard_data.json app/dashboard/public/dashboard_data.json data/logs/batch_health_log.jsonl"
        in workflow_text
    )

    # Indentation / structure checks.
    assert "\n  schedule:\n" in workflow_text
    assert "\n    - cron: \"30 0 * * *\"" in workflow_text
    assert "\n  scheduled-batch-run:\n" in workflow_text
    assert "\n    runs-on: ubuntu-latest" in workflow_text
    assert "\n    env:\n      PYTHONPATH: ." in workflow_text
    assert "\n    steps:\n      - name: Checkout repository" in workflow_text
    assert "\n        uses: actions/checkout@v4" in workflow_text
    assert "\n        run: python scripts/run_manual_batch.py" in workflow_text
    assert (
        "\n        run: python scripts/append_batch_health_log.py --tests-status passed --batch-status passed"
        in workflow_text
    )


def test_pr18_files_have_no_bidi_controls_and_use_lf_newlines() -> None:
    for file_path in TARGET_FILES:
        path = Path(file_path)
        raw = path.read_bytes()
        text = raw.decode("utf-8")

        assert "\r\n" not in text, f"{file_path} contains CRLF newlines"
        assert "\r" not in text, f"{file_path} contains CR newlines"
        for control_char in BIDI_CONTROLS:
            assert control_char not in text, (
                f"{file_path} contains bidi control U+{ord(control_char):04X}"
            )
