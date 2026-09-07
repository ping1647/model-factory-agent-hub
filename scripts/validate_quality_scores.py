"""Command-line entry point for offline quality-score reconciliation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agents.quality_score_validator import load_quality_rows, validate_quality_scores


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate reported quality scores against the disclosed formula")
    parser.add_argument("input", help="CSV or JSON input path")
    parser.add_argument("--output", help="Optional JSON output path; stdout is used when omitted")
    parser.add_argument("--tolerance", type=float, default=1e-8)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows, input_status = load_quality_rows(args.input)
    report = validate_quality_scores(
        rows,
        tolerance=args.tolerance,
        input_processing_status=input_status,
    )
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if report["validation_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

