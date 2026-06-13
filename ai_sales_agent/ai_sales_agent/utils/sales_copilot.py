import frappe
from frappe.utils import now


def build_copilot_context(handoff_name=None, ai_lead_name=None):
    """Gather context for copilot from AI Handoff and AI Lead.

    Returns a dict with: latest_message, lead_category, intent_type, opportunity
    """
    try:
        context = {
            "latest_message": "",
            "lead_category": "",
            "intent_type": "",
            "opportunity": "",
        }

        if handoff_name:
            h = frappe.get_doc("AI Handoff", handoff_name)
            ai_lead_name = ai_lead_name or h.lead
            # prefer handoff stored suggested reply/opportunity
            context["opportunity"] = h.get("opportunity") or ""

        if ai_lead_name:
            lead = frappe.get_doc("AI Lead", ai_lead_name)
            analysis = lead.get("analysis") or {}
            context["lead_category"] = (analysis.get("lead_category") or lead.get("lead_category") or "")
            context["intent_type"] = (analysis.get("intent_type") or lead.get("intent") or "")

            # fetch latest message from CRM Conversation
            conv = frappe.get_all(
                "CRM Conversation",
                filters={"contact": lead.get("contact")},
                fields=["message"],
                order_by="timestamp desc",
                limit=1,
            )
            if conv:
                context["latest_message"] = conv[0].get("message") or ""

            # opportunity already set from handoff; if not, try lead.opportunity
            if not context["opportunity"]:
                context["opportunity"] = lead.get("opportunity") or ""

        return context

    except Exception:
        frappe.log_error(frappe.get_traceback(), "build_copilot_context_error")
        return {
            "latest_message": "",
            "lead_category": "",
            "intent_type": "",
            "opportunity": "",
        }


def recommend_next_action(intent_or_context):
    """Map intent to a recommended next action string."""
    try:
        intent = ""
        if isinstance(intent_or_context, dict):
            intent = (intent_or_context.get("intent_type") or intent_or_context.get("intent") or "").lower()
        else:
            intent = (intent_or_context or "").lower()

        mapping = {
            "pricing": "Schedule Demo",
            "price": "Schedule Demo",
            "pricing inquiry": "Schedule Demo",
            "demo": "Book Meeting",
            "demo request": "Book Meeting",
            "implementation": "Assign Consultant",
            "implementation inquiry": "Assign Consultant",
            "support": "Create Support Ticket",
            "support request": "Create Support Ticket",
            "partnership": "Escalate To Business Development",
        }

        for k, v in mapping.items():
            if k in intent:
                return v

        # fallback heuristics
        if "demo" in intent:
            return "Book Meeting"
        if "price" in intent or "quote" in intent:
            return "Schedule Demo"

        return "Review and Reply"

    except Exception:
        frappe.log_error(frappe.get_traceback(), "recommend_next_action_error")
        return "Review and Reply"


def _generate_template_reply(context):
    """Simple template-based reply generation using context."""
    msg = (context.get("latest_message") or "").lower()
    intent = (context.get("intent_type") or "").lower()
    category = context.get("lead_category") or ""
    opp = context.get("opportunity") or ""

    # Basic templating by intent
    try:
        if "pricing" in intent or "price" in msg or "quote" in msg:
            return f"Thank you for your interest. Based on your requirements, we'd be happy to arrange a demo and share pricing options. {('Opportunity: ' + opp) if opp else ''}".strip()

        if "demo" in intent or "demo request" in intent or "demo" in msg:
            return "Thank you for reaching out. Please share your preferred date and time for a product demonstration."

        if "implementation" in intent or "implementation" in msg:
            return "We can assist with implementation planning. Please share your current system and expected timeline."

        if "support" in intent or "issue" in msg or "help" in msg:
            return "We're sorry to hear you're facing an issue. Please provide details and we'll create a support ticket and respond shortly."

        if "partnership" in intent or "partner" in msg:
            return "Thanks for your partnership interest. We'll connect you with our business development team to discuss next steps."

        # default
        return "Thank you for reaching out. We'll review your request and get back to you shortly."

    except Exception:
        frappe.log_error(frappe.get_traceback(), "_generate_template_reply_error")
        return "Thank you for reaching out; we'll get back to you shortly."


def generate_reply(handoff_name=None, ai_lead_name=None):
    """Generate suggested reply and next action for a handoff or lead.

    Saves values to `AI Handoff` when `handoff_name` provided.
    Returns dict {reply, next_action}
    """
    try:
        context = build_copilot_context(handoff_name=handoff_name, ai_lead_name=ai_lead_name)
        reply = _generate_template_reply(context)
        action = recommend_next_action(context)

        # Persist to handoff if provided
        if handoff_name:
            try:
                h = frappe.get_doc("AI Handoff", handoff_name)
                h.ai_suggested_reply = reply
                h.next_best_action = action
                h.db_set("ai_suggested_reply", reply, update_modified=True)
                h.db_set("next_best_action", action, update_modified=True)
            except Exception:
                frappe.log_error(frappe.get_traceback(), "generate_reply_persist_error")

        frappe.logger().info(f"SALES COPILOT GENERATED for {handoff_name or ai_lead_name}")
        return {"reply": reply, "next_action": action}

    except Exception:
        frappe.log_error(frappe.get_traceback(), "generate_reply_error")
        return {"reply": "", "next_action": ""}


@frappe.whitelist()
def get_ai_reply(handoff_name=None, ai_lead_name=None):
    """Return existing ai_suggested_reply and next_best_action for a handoff or generate on-the-fly."""
    try:
        if handoff_name:
            h = frappe.get_doc("AI Handoff", handoff_name)
            return {"reply": h.get("ai_suggested_reply") or "", "next_action": h.get("next_best_action") or ""}

        # fallback: generate from lead
        return generate_reply(handoff_name=handoff_name, ai_lead_name=ai_lead_name)

    except Exception:
        frappe.log_error(frappe.get_traceback(), "get_ai_reply_error")
        return {"reply": "", "next_action": ""}


@frappe.whitelist()
def refresh_ai_reply(handoff_name=None, ai_lead_name=None):
    """Force regenerate suggested reply and next action and persist to handoff if provided."""
    try:
        result = generate_reply(handoff_name=handoff_name, ai_lead_name=ai_lead_name)
        return result
    except Exception:
        frappe.log_error(frappe.get_traceback(), "refresh_ai_reply_error")
        return {"reply": "", "next_action": ""}
