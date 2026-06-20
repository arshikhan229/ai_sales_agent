import frappe

from ai_sales_agent.ai_sales_agent.utils.copilot_actions import (
    create_followups_for_risky_deals,
    move_opportunity,
    close_opportunity
)


@frappe.whitelist()
def ask(question):

    q = (question or "").lower()

    # ==========================
    # AI ACTIONS
    # ==========================

    if (
        "create followup" in q
        or "create followups" in q
    ):
        return {
            "type": "action",
            "result": create_followups_for_risky_deals()
        }

    if (
        "close crm-opp" in q
        or "close opportunity" in q
    ):

        opportunity = (
            question
            .replace("Close", "")
            .replace("close", "")
            .replace("Opportunity", "")
            .replace("opportunity", "")
            .strip()
        )

        return {
            "type": "action",
            "result": close_opportunity(
                opportunity
            )
        }

    if (
        "move crm-opp" in q
        or "move opportunity" in q
    ):

        parts = question.split(" to ")

        if len(parts) == 2:

            opportunity = (
                parts[0]
                .replace("Move", "")
                .replace("move", "")
                .replace("Opportunity", "")
                .replace("opportunity", "")
                .strip()
            )

            stage = parts[1].strip()

            return {
                "type": "action",
                "result": move_opportunity(
                    opportunity,
                    stage
                )
            }

    # ==========================
    # NATURAL LANGUAGE QUERIES
    # ==========================

    if any(
        x in q
        for x in [
            "attention",
            "follow up",
            "followup",
            "need attention"
        ]
    ):
        return get_attention_leads()

    if any(
        x in q
        for x in [
            "likely to close",
            "close soon",
            "best deals"
        ]
    ):
        return get_likely_to_close()

    if any(
        x in q
        for x in [
            "biggest",
            "largest opportunities"
        ]
    ):
        return get_biggest_opportunities()

    if any(
        x in q
        for x in [
            "stuck",
            "not moving"
        ]
    ):
        return get_stuck_opportunities()

    # ==========================
    # ORIGINAL QUERIES
    # ==========================

    if "hot lead" in q:
        return get_hot_leads()

    if "risk" in q:
        return get_risky_opportunities()

    if "followup" in q:
        return get_followups()

    if "whatsapp" in q:
        return get_whatsapp_leads()

    if "handoff" in q:
        return get_open_handoffs()

    if "forecast" in q:
        return get_forecast()

    return {
        "type": "message",
        "message": "I don't understand the question."
    }


def get_hot_leads():

    rows = frappe.get_all(
        "AI Lead",
        filters={
            "lead_category": "Hot"
        },
        fields=[
            "name",
            "lead_name",
            "intent_type"
        ],
        limit=20
    )

    return {
        "type": "table",
        "title": "Hot Leads",
        "rows": rows
    }


def get_risky_opportunities():

    rows = frappe.get_all(
        "Opportunity",
        filters={
            "custom_risk_level": "High"
        },
        fields=[
            "name",
            "custom_risk_level",
            "custom_win_probability"
        ]
    )

    return {
        "type": "table",
        "title": "Risky Opportunities",
        "rows": rows
    }


def get_followups():

    rows = frappe.get_all(
        "ToDo",
        filters={
            "status": "Open"
        },
        fields=[
            "name",
            "description",
            "allocated_to"
        ]
    )

    return {
        "type": "table",
        "title": "Open Followups",
        "rows": rows
    }


def get_whatsapp_leads():

    rows = frappe.get_all(
        "AI Lead",
        filters={
            "source": "WhatsApp"
        },
        fields=[
            "name",
            "lead_name",
            "intent_type"
        ]
    )

    return {
        "type": "table",
        "title": "WhatsApp Leads",
        "rows": rows
    }


def get_open_handoffs():

    rows = frappe.get_all(
        "AI Handoff",
        filters={
            "status": "Open"
        },
        fields=[
            "name",
            "assigned_to",
            "opportunity"
        ]
    )

    return {
        "type": "table",
        "title": "Open Handoffs",
        "rows": rows
    }


def get_forecast():

    from ai_sales_agent.ai_sales_agent.utils.revenue_forecast import (
        get_revenue_forecast
    )

    return {
        "type": "forecast",
        "data": get_revenue_forecast()
    }


def get_attention_leads():

    rows = frappe.get_all(
        "AI Handoff",
        filters={
            "status": "Open"
        },
        fields=[
            "lead",
            "assigned_to",
            "creation"
        ],
        order_by="creation asc",
        limit=20
    )

    return {
        "type": "table",
        "title": "Leads Needing Attention",
        "rows": rows
    }


def get_likely_to_close():

    rows = frappe.get_all(
        "Opportunity",
        filters={
            "custom_win_probability": [">=", 60]
        },
        fields=[
            "name",
            "custom_win_probability",
            "opportunity_amount"
        ],
        order_by="custom_win_probability desc"
    )

    return {
        "type": "table",
        "title": "Likely To Close",
        "rows": rows
    }


def get_biggest_opportunities():

    rows = frappe.get_all(
        "Opportunity",
        fields=[
            "name",
            "opportunity_amount",
            "custom_pipeline_stage"
        ],
        order_by="opportunity_amount desc",
        limit=20
    )

    return {
        "type": "table",
        "title": "Biggest Opportunities",
        "rows": rows
    }


def get_stuck_opportunities():

    rows = frappe.get_all(
        "Opportunity",
        filters={
            "custom_pipeline_stage": "Qualified"
        },
        fields=[
            "name",
            "opportunity_amount",
            "modified"
        ],
        order_by="modified asc"
    )

    return {
        "type": "table",
        "title": "Stuck Opportunities",
        "rows": rows
    }