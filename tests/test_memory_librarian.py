import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from agents.memory_librarian import run_memory_check


BASE_MATRIX = {
    "M5": {},
    "M6": {},
    "M7": {},
    "M13": {},
    "M14": {},
}


def build_complete_context():
    return {
        "model_registry_master": {"freshness": "fresh"},
        "model_checkpoint_latest": {"freshness": "fresh"},
        "changelog_master": {"freshness": "fresh"},
        "model_factor_matrix": {"freshness": "fresh"},
        "contradiction_log": {"freshness": "fresh"},
    }


def test_complete_context_supported_model_passes():
    context = build_complete_context()
    context["target_models"] = ["M5"]

    result = run_memory_check(context, BASE_MATRIX)

    assert result["passed"] is True
    assert result["severity"] == "Pass"
    assert result["missing_context_keys"] == []
    assert result["unsupported_model_ids"] == []


def test_missing_model_factor_matrix_fails():
    context = build_complete_context()
    context.pop("model_factor_matrix")

    result = run_memory_check(context, BASE_MATRIX)

    assert result["passed"] is False
    assert result["severity"] == "Fail"
    assert "model_factor_matrix" in result["missing_context_keys"]


def test_stale_changelog_master_warns():
    context = build_complete_context()
    context["changelog_master"] = {"freshness": "stale"}

    result = run_memory_check(context, BASE_MATRIX)

    assert result["passed"] is False
    assert result["severity"] == "Warning"
    assert "changelog_master" in result["stale_context_keys"]


def test_unsupported_model_fails():
    context = build_complete_context()
    context["target_models"] = ["M99"]

    result = run_memory_check(context, BASE_MATRIX)

    assert result["passed"] is False
    assert result["severity"] == "Fail"
    assert "M99" in result["unsupported_model_ids"]


def test_multiple_supported_models_pass():
    context = build_complete_context()
    context["target_models"] = ["M5", "M13", "M14"]

    result = run_memory_check(context, BASE_MATRIX)

    assert result["passed"] is True
    assert result["severity"] == "Pass"
    assert result["unsupported_model_ids"] == []
