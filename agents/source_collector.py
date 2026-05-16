"""Deterministic Source Collector scaffold for model-specific audit requirements."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

_REQUIREMENTS_PATH = Path(__file__).resolve().parents[1] / "data" / "source_requirements.json"


def _load_requirements() -> Dict[str, List[Dict[str, Any]]]:
    payload = json.loads(_REQUIREMENTS_PATH.read_text(encoding="utf-8"))
    return payload["models"]


def build_source_requirements(ticker: str, model_id: str) -> Dict[str, Any]:
    """Return deterministic source requirements for the given ticker/model pair."""
    normalized_model = model_id.strip().upper()
    requirements_by_model = _load_requirements()

    if normalized_model not in requirements_by_model:
        raise ValueError(f"Unsupported model_id: {model_id}")

    requirements = [dict(item) for item in requirements_by_model[normalized_model]]
    return {
        "ticker": ticker.strip().upper(),
        "model_id": normalized_model,
        "source_requirements": requirements,
    }
