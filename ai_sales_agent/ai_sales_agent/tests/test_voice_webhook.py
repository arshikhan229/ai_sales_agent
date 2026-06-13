import frappe
import importlib


def test_incoming_call_success(monkeypatch):
    # prepare a fake form_dict like Twilio would send
    frappe.form_dict = {
        "CallSid": "CA123",
        "From": "+15551234567",
        "To": "+15005550006",
        "CallStatus": "completed",
    }

    called = {}

    def fake_process_inbound_message(channel, message, phone, meta, reply_target=None):
        called['args'] = dict(channel=channel, message=message, phone=phone, meta=meta, reply_target=reply_target)
        return {"success": True}

    monkeypatch.setattr(
        "ai_sales_agent.ai_sales_agent.utils.channel_processor.process_inbound_message",
        fake_process_inbound_message,
    )

    # import here so module-level imports resolve with monkeypatch applied
    mod = importlib.import_module("ai_sales_agent.ai_sales_agent.voice.voice_webhook")
    resp = mod.incoming_call()

    assert "Thank you for calling" in resp
    assert called.get('args') and called['args']['channel'] == 'Voice'
