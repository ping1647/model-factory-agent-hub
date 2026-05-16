from __future__ import annotations

import json
from pathlib import Path

from scripts import run_manual_batch


def test_build_run_context_has_all_required_memory_keys():
    context = run_manual_batch.build_run_context(["M5", "M13"])

    assert set(context.keys()) == {
        "model_registry_master",
        "model_checkpoint_latest",
        "changelog_master",
        "model_factor_matrix",
        "contradiction_log",
        "target_models",
    }
    assert context["target_models"] == ["M5", "M13"]
    assert context["model_registry_master"]["freshness"] == "fresh"


def test_load_base_audits_skips_missing(tmp_path):
    (tmp_path / "TTEK.audit.json").write_text("{}", encoding="utf-8")
    audits = run_manual_batch.load_base_audits(examples_dir=tmp_path, tickers=("TTEK", "SOFI"))

    assert set(audits.keys()) == {"TTEK"}


def test_main_runs_and_writes_dashboard_outputs(tmp_path, monkeypatch):
    root = Path(__file__).resolve().parents[1]
    output_runs = tmp_path / "runs"
    output_dashboard = tmp_path / "dashboard" / "latest_dashboard_data.json"
    output_public = tmp_path / "public" / "dashboard_data.json"

    monkeypatch.setattr(
        "sys.argv",
        [
            "run_manual_batch.py",
            "--run-id",
            "manual-test-001",
            "--run-date",
            "2026-05-16",
            "--run-output-dir",
            str(output_runs),
            "--dashboard-output-path",
            str(output_dashboard),
            "--dashboard-public-path",
            str(output_public),
            "--watchlist-path",
            str(root / "data" / "watchlists" / "master_watchlist.json"),
            "--market-inputs-path",
            str(root / "data" / "market_inputs" / "manual_batch_market_inputs.json"),
        ],
    )

    exit_code = run_manual_batch.main()
    assert exit_code == 0

    assert output_dashboard.exists()
    assert output_public.exists()
    assert output_runs.exists()

    payload = json.loads(output_dashboard.read_text(encoding="utf-8"))
    assert "summary" in payload
