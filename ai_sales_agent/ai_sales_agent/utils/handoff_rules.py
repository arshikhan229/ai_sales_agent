import frappe
from ai_sales_agent.ai_sales_agent.utils.sales_copilot import (
    generate_reply
)

from ai_sales_agent.ai_sales_agent.utils.handoff_engine import (
    create_followup_todo
)


SALES_INTENT_KEYWORDS = [
    "pricing",
    "proposal",
    "quotation",
    "quote",
    "demo",
    "call",
    "meeting",
    "implementation",
]


def should_handoff(analysis):
    """
    Return True when lead is Hot OR intent contains sales keywords.
    analysis: dict returned by AI analysis
    """
    if not analysis:
        return False

    lead_category = (analysis.get("lead_category") or "").lower()
    if "hot" in lead_category:
        return True

    intent = (analysis.get("intent_type") or "").lower()
    for kw in SALES_INTENT_KEYWORDS:
        if kw in intent:
            return True

    # Also check raw message intent/content
    message = (analysis.get("message") or "").lower()
    for kw in SALES_INTENT_KEYWORDS:
        if kw in message:
            return True

    return False


def assign_salesperson():
    """Return first enabled System User (exclude Administrator/Guest).

    Queries `tabUser` for enabled system users and returns the first match.
    Falls back to `Administrator` when none found.
    Detailed logging is emitted for observability.
    """
    try:
        users = frappe.get_all(
            "User",
            filters={
                "enabled": 1,
                "user_type": "System User",
            },
            fields=["name"],
            order_by="creation asc",
            limit=100,
        )

        for u in users:
            name = u.name
            if name in ("Administrator", "Guest"):
                continue

            frappe.logger().info(
                f"AI HANDOFF ASSIGNED => {name}"
            )
            return name

        frappe.logger().warning("AI HANDOFF: No suitable system user found, falling back to Administrator")
        return "Administrator"

    except Exception:
        frappe.log_error(frappe.get_traceback(), "ASSIGN SALESPERSON ERROR")
        return "Administrator"


def create_handoff(lead, contact, channel, conversation, opportunity, analysis):
    """
    Create AI Handoff record if not duplicate. Returns document.
    """
    if not (lead or contact or channel):
        return None

    # Avoid duplicates: open/assigned/in progress for same lead+opportunity
    filters = {"lead": lead}
    if opportunity:
        filters["opportunity"] = opportunity

    existing = frappe.get_all(
        "AI Handoff",
        filters=filters,
        fields=["name", "status"],
        limit=1,
    )

    # Log creating attempt (includes opportunity/contact/channel for debugging)
    try:
        frappe.logger().info(
            f"""
            CREATING HANDOFF
            lead={lead}
            contact={contact}
            channel={channel}
            opportunity={opportunity}
            """
        )
    except Exception:
        # best-effort
        frappe.logger().info("CREATING HANDOFF => <failed to serialize details>")

    if existing:
        try:
            frappe.logger().info(f"HANDOFF ALREADY EXISTS => {existing[0].name}")
        except Exception:
            frappe.logger().info("HANDOFF ALREADY EXISTS => <unserializable>")

        name = existing[0].name
        doc = frappe.get_doc("AI Handoff", name)
        if doc.status != "Closed":
            return name

    from ai_sales_agent.ai_sales_agent.utils.lead_assignment import (
        assign_lead
    )

    assigned = assign_lead(
        lead,
        opportunity
    )

    handoff = frappe.get_doc({
        "doctype": "AI Handoff",
        "lead": lead,
        "contact": contact,
        "channel": channel,
        "assigned_to": assigned,
        "status": "Open",
        "priority": "High",
        "conversation": conversation,
        "opportunity": opportunity,
        "created_from_intent": analysis.get("intent_type"),
        "created_from_category": analysis.get("lead_category"),
        "notes": analysis.get("summary") or "",
    })

    try:
        frappe.logger().info(f"CREATING HANDOFF => lead={lead}")
        handoff.insert(ignore_permissions=True)

        # Create follow-up task for salesperson
        if opportunity:
            try:
                todo = create_followup_todo(
                    opportunity=opportunity,
                    assigned_user=assigned,
                    ai_lead=lead
                )

                frappe.logger().info(f"FOLLOWUP TODO CREATED => {todo}")

            except Exception:
                frappe.log_error(
                    frappe.get_traceback(),
                    "FOLLOWUP TODO ERROR"
                )

        frappe.db.commit()

        frappe.db.commit()

        try:

            generate_reply(
                handoff_name=handoff.name,
                ai_lead_name=lead
            )

            frappe.logger().info(
                f"COPILOT GENERATED => {handoff.name}"
            )

        except Exception:

            frappe.log_error(
                frappe.get_traceback(),
                "COPILOT GENERATION ERROR"
            )

        frappe.logger().info(
            f"HANDOFF CREATED => {handoff.name}"
        )

        return handoff.name

    except Exception:
        frappe.logger().error(f"HANDOFF ERROR => {frappe.get_traceback()}")
        frappe.log_error(frappe.get_traceback(), "HANDOFF INSERT ERROR")
        raise


def debug_inspect_lead(lead_name):
    """Temporary helper for debugging via `bench execute`.

    Returns a dict containing the lead, its analysis, should_handoff result,
    and any existing AI Handoff records for the lead.
    """
    try:
        lead = frappe.get_doc("AI Lead", lead_name).as_dict()
    except Exception as e:
        return {"error": str(e)}

    analysis = lead.get("analysis")
    try:
        handoff_decision = should_handoff(analysis)
    except Exception as e:
        handoff_decision = f"error: {e}"

    existing = frappe.get_all(
        "AI Handoff",
        filters={"lead": lead_name},
        fields=["name", "status", "opportunity"],
    )

    return {
        "lead": lead,
        "analysis": analysis,
        "should_handoff": handoff_decision,
        "existing_handoffs": existing,
    }
