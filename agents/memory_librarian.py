"""Deterministic Memory Librarian scaffold for pre-batch context checks."""

from __future__ import annotations

from typing import Any


DEFAULT_REQUIRED_CONTEXT_KEYS = [
    "model_registry_master",
    "model_checkpoint_latest",
    "changelog_master",
    "model_factor_matrix",
    "contradiction_log",
]


def run_memory_check(
    run_context: dict[str, Any],
    model_factor_matrix: dict[str, Any],
    required_context_keys: list[str] | None = None,
) -> dict[str, Any]:
    """Validate run_context completeness, freshness, and model support."""
    required_keys = list(required_context_keys or DEFAULT_REQUIRED_CONTEXT_KEYS)

    missing_context_keys: list[str] = []
    stale_context_keys: list[str] = []
    unsupported_model_ids: list[str] = []
    warnings: list[str] = []
    failures: list[str] = []

    for key in required_keys:
        if key not in run_context:
            missing_context_keys.append(key)
            failures.append(f"Missing required context key: {key}")
            continue

        value = run_context.get(key)
        if isinstance(value, dict) and value.get("freshness") == "stale":
            stale_context_keys.append(key)
            warnings.append(f"Stale context detected: {key}")

    target_models = run_context.get("target_models", [])
    if isinstance(target_models, list):
        for model_id in target_models:
            if model_id not in model_factor_matrix:
                normalized = str(model_id)
                unsupported_model_ids.append(normalized)
                failures.append(f"Unsupported target model: {normalized}")

    if missing_context_keys or unsupported_model_ids:
        severity = "Fail"
        next_action = (
            "Add missing required context and remove or define unsupported target models "
            "before running any investing batch."
        )
    elif stale_context_keys:
        severity = "Warning"
        next_action = (
            "Refresh stale context inputs before proceeding to improve evidence quality."
        )
    else:
        severity = "Pass"
        next_action = "Proceed: required memory context is complete, fresh, and supported."

    return {
        "passed": severity == "Pass",
        "missing_context_keys": missing_context_keys,
        "stale_context_keys": stale_context_keys,
        "unsupported_model_ids": unsupported_model_ids,
        "warnings": warnings,
        "failures": failures,
        "severity": severity,
        "next_action": next_action,
    }
