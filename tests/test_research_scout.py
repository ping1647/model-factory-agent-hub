import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from agents.research_scout import build_research_summary_skeleton
from agents.source_collector import build_source_requirements


TEST_CASES = [
    ("SOFI", "M5"),
    ("TTEK", "M13"),
    ("HIMS", "M6"),
]


def test_research_summary_scaffold_defaults_and_missing_data():
    for ticker, model_id in TEST_CASES:
        source_payload = build_source_requirements(ticker, model_id)
        source_requirements = source_payload["source_requirements"]

        result = build_research_summary_skeleton(ticker, model_id, source_requirements)

        assert result["ticker"] == ticker
        assert result["model_id"] == model_id
        assert result["preliminary_decision"] == "Wait"
        assert result["evidence_quality"] == "Missing Data"
        assert result["source_checklist"] == source_requirements

        required_source_types = [
            item["source_type"]
            for item in source_requirements
            if item.get("required") is True
        ]
        assert result["missing_data"] == required_source_types
