from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_DASHBOARD_PATH = Path("data/dashboard/latest_dashboard_data.json")
DEFAULT_LOG_PATH = Path("data/logs/batch_health_log.jsonl")


def _safe_int(value: Any) -> int:
    return value if isinstance(value, int) else 0


def _read_dashboard_summary(dashboard_path: Path) -> tuple[bool, dict[str, int], str]:
    summary = {
        "summary_total_count": 0,
        "summary_pass_count": 0,
        "summary_fail_count": 0,
        "summary_needs_audit_count": 0,
    }

    if not dashboard_path.exists():
        return False, summary, "dashboard JSON missing"

    try:
        payload = json.loads(dashboard_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return False, summary, f"dashboard JSON malformed or unreadable: {exc}"

    dashboard_summary = payload.get("summary") if isinstance(payload, dict) else None
    if not isinstance(dashboard_summary, dict):
        return False, summary, "dashboard summary missing or invalid"

    summary["summary_total_count"] = _safe_int(dashboard_summary.get("total_count"))
    summary["summary_pass_count"] = _safe_int(dashboard_summary.get("pass_count"))
    summary["summary_fail_count"] = _safe_int(dashboard_summary.get("fail_count"))
    summary["summary_needs_audit_count"] = _safe_int(dashboard_summary.get("needs_audit_count"))
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
        **summary,
        "notes": note,
    }

    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")

    return row


def main() -> None:
    parser = argparse.ArgumentParser(description="Append one health log record for batch runs")
    parser.add_argument("--tests-status", required=True)
    parser.add_argument("--batch-status", required=True)
    args = parser.parse_args()

    append_batch_health_log(tests_status=args.tests_status, batch_status=args.batch_status)


if __name__ == "__main__":
    main()
