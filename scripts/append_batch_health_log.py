from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_DASHBOARD_PATH = Path("data/dashboard/latest_dashboard_data.json")
DEFAULT_LOG_PATH = Path("data/logs/batch_health_log.jsonl")


REQUIRED_SUMMARY_KEYS = {
    "summary_total_count": "total_count",
    "summary_pass_count": "pass_count",
    "summary_fail_count": "fail_count",
    "summary_needs_audit_count": "needs_audit_count",
}


def _safe_int(value: Any) -> int:
    if isinstance(value, bool):
        return 0
    if isinstance(value, int):
        return value
    return 0


def _empty_summary() -> dict[str, int]:
    return {
        "summary_total_count": 0,
        "summary_pass_count": 0,
        "summary_fail_count": 0,
        "summary_needs_audit_count": 0,
    }


def _read_dashboard_summary(dashboard_path: Path) -> tuple[bool, dict[str, int], str]:
    summary = _empty_summary()

    if not dashboard_path.exists():
        return False, summary, "dashboard JSON missing"

    try:
        payload = json.loads(dashboard_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return False, summary, f"dashboard JSON malformed or unreadable: {exc}"

    if not isinstance(payload, dict):
        return False, summary, "dashboard payload is not an object"

    dashboard_summary = payload.get("summary")
    if not isinstance(dashboard_summary, dict):
        return False, summary, "dashboard summary missing or invalid"

    for out_key, in_key in REQUIRED_SUMMARY_KEYS.items():
        summary[out_key] = _safe_int(dashboard_summary.get(in_key))

    return True, summary, ""


def append_batch_health_log(
    tests_status: str,
    batch_status: str,
    dashboard_path: Path = DEFAULT_DASHBOARD_PATH,
    log_path: Path = DEFAULT_LOG_PATH,
) -> dict[str, Any]:
    dashboard_exists, summary, note = _read_dashboard_summary(dashboard_path)

    row: dict[str, Any] = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "workflow_name": os.getenv("GITHUB_WORKFLOW", ""),
        "trigger_event": os.getenv("GITHUB_EVENT_NAME", ""),
        "github_run_id": os.getenv("GITHUB_RUN_ID", ""),
        "github_run_number": os.getenv("GITHUB_RUN_NUMBER", ""),
        "github_sha": os.getenv("GITHUB_SHA", ""),
        "github_ref": os.getenv("GITHUB_REF", ""),
        "tests_status": tests_status,
        "batch_status": batch_status,
        "dashboard_path": str(dashboard_path),
        "dashboard_exists": dashboard_exists,
        "summary_total_count": summary["summary_total_count"],
        "summary_pass_count": summary["summary_pass_count"],
        "summary_fail_count": summary["summary_fail_count"],
        "summary_needs_audit_count": summary["summary_needs_audit_count"],
        "notes": note,
    }

    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")

    return row


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Append one health log record for batch runs")
    parser.add_argument("--tests-status", required=True)
    parser.add_argument("--batch-status", required=True)
    return parser


def main() -> None:
    parser = _build_arg_parser()
    args = parser.parse_args()
    append_batch_health_log(tests_status=args.tests_status, batch_status=args.batch_status)


if __name__ == "__main__":
    main()
