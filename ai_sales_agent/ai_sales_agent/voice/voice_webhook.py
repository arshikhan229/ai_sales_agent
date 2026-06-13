import frappe

from .voice_twiml import simple_say_response
from ai_sales_agent.ai_sales_agent.utils.channel_processor import (
    process_inbound_message,
)
from .voice_handler import normalize_phone, build_call_metadata, create_or_get_lead


@frappe.whitelist(allow_guest=True)
def incoming_call():
    """Twilio incoming call webhook.

    Expected form fields (sent by Twilio): CallSid, From, To, CallStatus.
    This function normalizes the caller number, delegates creation/updating
    of leads/handoffs to `process_inbound_message` (which centralises
    inbound-channel processing), logs comprehensively, and returns a small
    TwiML response to Twilio.
    """
    try:
        data = frappe.form_dict or {}

        call_sid = data.get("CallSid") or ""
        caller = data.get("From") or ""
        to_number = data.get("To") or ""
        call_status = data.get("CallStatus") or ""

        # Normalize caller phone number
        caller = normalize_phone(caller)

        frappe.logger().info(f"VOICE INCOMING => {caller} -> {to_number} sid={call_sid} status={call_status}")

        if not caller:
            frappe.log_error("EMPTY CALLER NUMBER", "VOICE WEBHOOK")
            # Return a neutral TwiML so Twilio doesn't retry aggressively
            return simple_say_response("Thank you for calling. Your call has been logged.")

        # Build metadata for reporting and downstream processing
        meta = build_call_metadata(data)

        # Delegate to channel processor which will create/merge Leads, Conversations and Handoffs
        result = process_inbound_message(
            channel="Voice",
            message="Incoming voice call",
            phone=caller,
            meta=meta,
            reply_target={"phone": caller},
        )

        if result.get("success"):
            frappe.logger().info("VOICE FLOW SUCCESS")
            return simple_say_response("Thank you for calling. Your call has been logged and a representative will contact you shortly.")

        if result.get("skipped"):
            # Quietly acknowledge
            return simple_say_response("Thank you for calling. Your call has been logged.")

        frappe.log_error(frappe.as_json(result), "VOICE PROCESSOR FAILED")
        return simple_say_response("Thank you for calling. Your call has been logged.")

    except Exception:
        frappe.log_error(frappe.get_traceback(), "VOICE WEBHOOK ERROR")
        return simple_say_response("Thank you for calling. Your call has been logged.")
