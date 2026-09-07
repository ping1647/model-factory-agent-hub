"""One-command synthetic readiness, export, and reopen-validation workflow."""

from __future__ import annotations

import argparse, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))

from agents.report_readiness import aggregate_report_readiness, apply_delivery_qa
from agents.synthetic_report_exporter import export_pdf, export_xlsx, inspect_pdf, inspect_xlsx


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--output-dir", default="artifacts/synthetic_demo")
    args = parser.parse_args()
    dataset = json.loads(Path(args.input).read_text(encoding="utf-8"))
    report = aggregate_report_readiness(dataset)
    output = Path(args.output_dir); output.mkdir(parents=True, exist_ok=True)
    xlsx, pdf = output / "SYNTHETIC_DEMO.xlsx", output / "SYNTHETIC_DEMO.pdf"
    export_xlsx(report, xlsx); export_pdf(report, pdf)
    checks = [inspect_xlsx(xlsx, report), *inspect_pdf(pdf, report)]
    report = apply_delivery_qa(report, checks)
    # Re-export final dataset, then verify machine-readable consistency once more.
    export_xlsx(report, xlsx); export_pdf(report, pdf)
    final_checks = [inspect_xlsx(xlsx, report), *inspect_pdf(pdf, report)]
    result = {"validated_dataset": report, "artifact_reopen_checks": final_checks}
    (output / "SYNTHETIC_DEMO.validated.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    print(json.dumps({"report": str(output / "SYNTHETIC_DEMO.validated.json"), "excel": str(xlsx), "pdf": str(pdf), "checks": final_checks}, ensure_ascii=False))
    return 0 if all(c["result"] == "PASS" for c in final_checks) else 2


if __name__ == "__main__": raise SystemExit(main())
