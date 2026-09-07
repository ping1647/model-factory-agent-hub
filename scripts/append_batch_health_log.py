"""Append one batch health event to a JSONL log."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_WORKFLOW_NAME = "Scheduled Batch Run"
DEFAULT_DASHBOARD_PATH = Path("data/dashboard/latest_dashboard_data.json")
DEFAULT_LOG_PATH = Path("data/logs/batch_health_log.jsonl")


def _to_int(value: Any) -> int:
    """Best-effort integer conversion with safe fallback."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _read_dashboard_summary(dashboard_path: Path) -> dict[str, Any]:
    """Return dashboard existence and summary counts with robust error handling."""
    if not dashboard_path.exists():
        return {
            "dashboard_exists": False,
            "summary_total_count": 0,
            "summary_pass_count": 0,
            "summary_fail_count": 0,
            "summary_needs_audit_count": 0,
            "notes": "Dashboard file does not exist.",
        }

    try:
        raw_text = dashboard_path.read_text(encoding="utf-8")
    except OSError as exc:
        return {
            "dashboard_exists": True,
            "summary_total_count": 0,
            "summary_pass_count": 0,
            "summary_fail_count": 0,
            "summary_needs_audit_count": 0,
            "notes": f"Dashboard file unreadable: {exc}",
        }

    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        return {
            "dashboard_exists": True,
            "summary_total_count": 0,
            "summary_pass_count": 0,
            "summary_fail_count": 0,
            "summary_needs_audit_count": 0,
            "notes": f"Dashboard JSON malformed: {exc}",
        }

    if not isinstance(payload, dict):
        return {
            "dashboard_exists": True,
            "summary_total_count": 0,
            "summary_pass_count": 0,
            "summary_fail_count": 0,
            "summary_needs_audit_count": 0,
            "notes": "Dashboard JSON root is not an object.",
        }

    summary = payload.get("summary")
    if not isinstance(summary, dict):
        summary = {}

    return {
        "dashboard_exists": True,
        "summary_total_count": _to_int(summary.get("total_count", 0)),
        "summary_pass_count": _to_int(summary.get("pass_count", 0)),
        "summary_fail_count": _to_int(summary.get("fail_count", 0)),
        "summary_needs_audit_count": _to_int(summary.get("needs_audit_count", 0)),
        "notes": "ok",
    }


def append_batch_health_log(tests_status: str, batch_status: str) -> dict[str, Any]:
    """Build a record and append it as a single JSON line."""
    dashboard_summary = _read_dashboard_summary(DEFAULT_DASHBOARD_PATH)

    record = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "workflow_name": DEFAULT_WORKFLOW_NAME,
        "trigger_event": os.getenv("GITHUB_EVENT_NAME", "manual"),
        "github_run_id": os.getenv("GITHUB_RUN_ID", ""),
        "github_run_number": os.getenv("GITHUB_RUN_NUMBER", ""),
        "github_sha": os.getenv("GITHUB_SHA", ""),
        "github_ref": os.getenv("GITHUB_REF", ""),
        "tests_status": tests_status,
        "batch_status": batch_status,
        "dashboard_path": str(DEFAULT_DASHBOARD_PATH),
        **dashboard_summary,
    }

    DEFAULT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with DEFAULT_LOG_PATH.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(record, ensure_ascii=False) + "\n")

    return record


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tests-status", required=True, help="Outcome of tests step")
    parser.add_argument("--batch-status", required=True, help="Outcome of batch step")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    append_batch_health_log(
        tests_status=args.tests_status,
        batch_status=args.batch_status,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
