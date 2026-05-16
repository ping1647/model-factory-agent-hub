import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from agents.source_collector import build_source_requirements


@pytest.mark.parametrize(
    "ticker,model_id,expected_types",
    [
        ("SOFI", "M5", ["deposits_and_funding_mix", "net_interest_margin_trend", "credit_quality_nco_and_delinquency", "capital_ratio_and_liquidity", "sbc_and_share_dilution", "fair_value_and_accounting_risk"]),
        ("HIMS", "M6", ["fda_and_regulatory_updates", "product_and_pipeline_progress", "reimbursement_and_payer_risk", "safety_and_litigation_exposure"]),
        ("TTEK", "M13", ["backlog_and_project_awards", "pfas_and_water_regulatory_developments", "customer_concentration_exposure", "project_timing_and_guidance"]),
        ("ERII", "M13", ["backlog_and_project_awards", "pfas_and_water_regulatory_developments", "customer_concentration_exposure", "project_timing_and_guidance"]),
        ("NVDA", "M7", ["segment_revenue_mix", "gross_margin_drivers", "customer_concentration", "supply_chain_and_capacity", "export_control_and_regulatory"]),
        ("VST", "M14", ["ppa_and_contract_quality", "regulatory_and_rate_case", "capex_and_debt_funding", "data_center_load_and_customer_demand"]),
    ],
)
def test_build_source_requirements_by_model(ticker, model_id, expected_types):
    result = build_source_requirements(ticker, model_id)
    assert result["ticker"] == ticker
    assert result["model_id"] == model_id

    types = [item["source_type"] for item in result["source_requirements"]]
    assert types == expected_types
    assert all(item["required"] is True for item in result["source_requirements"])


def test_unsupported_model_raises_value_error():
    with pytest.raises(ValueError):
        build_source_requirements("SOFI", "M99")
