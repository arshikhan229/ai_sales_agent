import frappe
import importlib


def test_scan_and_send_followups(monkeypatch):
    # Monkeypatch settings single
    class DummySettings:
        auto_followup_enabled = True
        followup_delay_days = 1
        max_followup_attempts = 3

    monkeypatch.setattr(frappe, "get_single", lambda *a, **k: DummySettings())

    # Create a fake stale handoff returned by SQL
    fake_handoffs = [
        {
            "name": "H1",
            "lead": "L1",
            "contact": "+15550001111",
            "status": "Assigned",
            "followup_count": 0,
            "last_followup_at": None,
            "next_followup_due": None,
            "creation": "2026-01-01 00:00:00",
        }
    ]

    monkeypatch.setattr(
        frappe.db, "sql", lambda *a, **k: fake_handoffs
    )

    called = {}

    def fake_send_reply(channel=None, contact=None, message=None, handoff_name=None, subject=None):
        called.setdefault("calls", []).append({"channel": channel, "contact": contact})
        return {"success": True, "sent": True}

    monkeypatch.setattr(
        "ai_sales_agent.ai_sales_agent.utils.reply_dispatcher.send_reply",
        fake_send_reply,
    )

    mod = importlib.import_module("ai_sales_agent.ai_sales_agent.followup.followup_engine")
    res = mod.scan_and_send_followups()

    assert res.get("candidates") == 1
    assert res.get("sent") >= 1
    assert called.get("calls")
