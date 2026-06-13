import importlib
import frappe


def test_scheduler_import():
    mod = importlib.import_module("ai_sales_agent.ai_sales_agent.followup.followup_scheduler")
    assert hasattr(mod, "run_daily_followups")


def test_get_settings_keys():
    mod = importlib.import_module("ai_sales_agent.ai_sales_agent.followup.followup_engine")
    s = mod._get_settings()
    assert isinstance(s, dict)
    assert "auto_followup_enabled" in s
    assert "followup_delay_days" in s
    assert "max_followup_attempts" in s


def test_scan_disabled_by_settings(monkeypatch):
    # return settings with auto_followup_enabled False
    class DummySettings:
        auto_followup_enabled = False

    monkeypatch.setattr(frappe, "get_single", lambda *a, **k: DummySettings())
    mod = importlib.import_module("ai_sales_agent.ai_sales_agent.followup.followup_engine")
    res = mod.scan_and_send_followups()
    assert res.get("status") == "disabled"
