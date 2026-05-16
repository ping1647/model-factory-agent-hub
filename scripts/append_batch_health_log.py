"""Append a health log row for scheduled/manual batch runs.

The script is intentionally standard-library only so it can run in GitHub
Actions without adding project dependencies. It is defensive by design:
missing or malformed dashboard JSON should be logged, not crash the workflow.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_DASHBOARD_PATH = Path("data/dashboard/latest_dashboard_data.json")
DEFAULT_LOG_PATH = Path("data/logs/batch_health_log.jsonl")


def _utc_now_iso() -> str:
    """Return an ISO-8601 UTC timestamp with a Z suffix."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _env(name: str, default: str = "") -> str:
    """Read an environment variable with a predictable string default."""
    return os.environ.get(name, default)


def _empty_summary() -> dict[str, int | None]:
    """Return default summary fields used when dashboard data is unavailable."""
    return {
        "summary_total_count": None,
        "summary_pass_count": None,
        "summary_fail_count": None,
        "summary_needs_audit_count": None,
    }


def load_dashboard_summary(dashboard_path: Path) -> tuple[bool, dict[str, int | None], list[str]]:
    """Load dashboard summary counts.

    Returns:
        A tuple of:
        - dashboard_exists: whether the file exists
        - summary: normalized summary fields
        - notes: non-fatal warnings to write into the health log
    """
    notes: list[str] = []
    summary = _empty_summary()

    if not dashboard_path.exists():
        notes.append(f"dashboard JSON not found: {dashboard_path}")
        return False, summary, notes

    try:
        payload: dict[str, Any] = json.loads(dashboard_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        notes.append(f"dashboard JSON malformed: {exc}")
        return True, summary, notes
    except OSError as exc:
        notes.append(f"dashboard JSON unreadable: {exc}")
        return True, summary, notes

    raw_summary = payload.get("summary")
    if not isinstance(raw_summary, dict):
        notes.append("dashboard JSON missing object field: summary")
        return True, summary, notes

    summary["summary_total_count"] = _as_optional_int(raw_summary.get("total_count"))
    summary["summary_pass_count"] = _as_optional_int(raw_summary.get("pass_count"))
    summary["summary_fail_count"] = _as_optional_int(raw_summary.get("fail_count"))
    summary["summary_needs_audit_count"] = _as_optional_int(raw_summary.get("needs_audit_count"))

    return True, summary, notes


def _as_optional_int(value: Any) -> int | None:
    """Convert a value to int when safe, otherwise return None."""
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def build_health_log_row(
    *,
    tests_status: str,
    batch_status: str,
    dashboard_path: Path = DEFAULT_DASHBOARD_PATH,
) -> dict[str, Any]:
    """Build one health-log row from environment metadata and dashboard summary."""
    dashboard_exists, summary, notes = load_dashboard_summary(dashboard_path)

    row: dict[str, Any] = {
        "timestamp_utc": _utc_now_iso(),
        "workflow_name": _env("GITHUB_WORKFLOW", "local"),
        "trigger_event": _env("GITHUB_EVENT_NAME", "local"),
        "github_run_id": _env("GITHUB_RUN_ID"),
        "github_run_number": _env("GITHUB_RUN_NUMBER"),
        "github_sha": _env("GITHUB_SHA"),
        "github_ref": _env("GITHUB_REF"),
        "tests_status": tests_status,
        "batch_status": batch_status,
        "dashboard_path": str(dashboard_path),
        "dashboard_exists": dashboard_exists,
        "notes": notes,
    }
    row.update(summary)
    return row


def append_health_log_row(row: dict[str, Any], log_path: Path = DEFAULT_LOG_PATH) -> Path:
    """Append one JSON object as one JSONL row."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True))
        handle.write("\n")
    return log_path


def append_batch_health_log(
    *,
    tests_status: str,
    batch_status: str,
    dashboard_path: Path = DEFAULT_DASHBOARD_PATH,
    log_path: Path = DEFAULT_LOG_PATH,
) -> Path:
    """Build and append a batch health log row."""
    row = build_health_log_row(
        tests_status=tests_status,
        batch_status=batch_status,
        dashboard_path=dashboard_path,
    )
    return append_health_log_row(row, log_path=log_path)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Append a batch health log row.")
    parser.add_argument("--tests-status", required=True, help="Outcome of the test step.")
    parser.add_argument("--batch-status", required=True, help="Outcome of the batch step.")
    parser.add_argument(
        "--dashboard-path",
        default=str(DEFAULT_DASHBOARD_PATH),
        help="Path to latest dashboard JSON.",
    )
    parser.add_argument(
        "--log-path",
        default=str(DEFAULT_LOG_PATH),
        help="Path to health log JSONL output.",
    )
    return parser.parse_args()


def main() -> int:
    """CLI entry point."""
    args = parse_args()
    append_batch_health_log(
        tests_status=args.tests_status,
        batch_status=args.batch_status,
        dashboard_path=Path(args.dashboard_path),
        log_path=Path(args.log_path),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
