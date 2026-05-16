"""Append a single batch health event to the JSONL audit log."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

DEFAULT_WORKFLOW_NAME = "Scheduled Batch Run"
DEFAULT_DASHBOARD_PATH = Path("data/dashboard/latest_dashboard_data.json")
DEFAULT_LOG_PATH = Path("data/logs/batch_health_log.jsonl")


def _read_dashboard_summary(dashboard_path: Path) -> Dict[str, Any]:
    """Safely read dashboard summary counts from JSON if available."""
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
        raw = json.loads(dashboard_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return {
            "dashboard_exists": True,
            "summary_total_count": 0,
            "summary_pass_count": 0,
            "summary_fail_count": 0,
            "summary_needs_audit_count": 0,
            "notes": f"Dashboard JSON malformed or unreadable: {exc}",
        }

    summary = raw.get("summary", {}) if isinstance(raw, dict) else {}
    return {
        "dashboard_exists": True,
        "summary_total_count": int(summary.get("total_count", 0) or 0),
        "summary_pass_count": int(summary.get("pass_count", 0) or 0),
        "summary_fail_count": int(summary.get("fail_count", 0) or 0),
        "summary_needs_audit_count": int(summary.get("needs_audit_count", 0) or 0),
        "notes": "ok",
    }


def append_batch_health_log(tests_status: str, batch_status: str) -> Dict[str, Any]:
    """Build and append one health event record into JSONL log."""
    dashboard_info = _read_dashboard_summary(DEFAULT_DASHBOARD_PATH)

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
        **dashboard_info,
    }

    DEFAULT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with DEFAULT_LOG_PATH.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    return record


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tests-status", required=True)
    parser.add_argument("--batch-status", required=True)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    append_batch_health_log(tests_status=args.tests_status, batch_status=args.batch_status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
