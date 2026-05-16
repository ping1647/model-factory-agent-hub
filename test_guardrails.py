import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from agents.risk_agent import apply_risk_rules
from agents.dashboard_agent import to_dashboard_card

def load_example(name):
    return json.loads((ROOT / "data" / "examples" / name).read_text())

def test_erii_risk_blocked_not_buy():
    audit = apply_risk_rules(load_example("ERII.audit.json"))
    assert audit["decision"] in ["Wait", "Risk-Blocked"]
    assert "guidance withdrawn" in " ".join(audit["blocked_by"]).lower()

def test_ttek_starter_not_heavy_buy():
    audit = apply_risk_rules(load_example("TTEK.audit.json"))
    assert audit["decision"] == "Starter"
    assert audit["position_class"] != "Core Heavy Buy"

def test_sofi_high_beta_not_core():
    audit = apply_risk_rules(load_example("SOFI.audit.json"))
    assert "High-Beta" in audit["position_class"] or "Satellite" in audit["position_class"]

def test_dashboard_card_has_risk_color():
    audit = apply_risk_rules(load_example("ERII.audit.json"))
    card = to_dashboard_card(audit)
    assert card["risk_color"] == "Orange"
    assert card["status"] == "Risk-Blocked"
