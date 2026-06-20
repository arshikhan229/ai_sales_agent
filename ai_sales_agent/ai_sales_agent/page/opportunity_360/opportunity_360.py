import frappe
from frappe.utils import flt


SYSTEM_FIELDS = {
    "name",
    "creation",
    "modified",
    "owner",
    "docstatus",
    "idx",
}


@frappe.whitelist()
def get_opportunity_360(opportunity):

    if not opportunity:
        return {}

    opp = _get_opportunity(opportunity)

    if not opp:
        return {}

    ai_lead = _get_ai_lead(opp)
    handoffs = _get_handoffs(opportunity)
    followups = _get_followups(opportunity)
    emails = _get_emails(opportunity, ai_lead)
    conversations = _get_conversations(ai_lead)

    whatsapp_messages = [
        row for row in conversations
        if (row.get("channel") or "").lower() == "whatsapp"
    ]

    win_probability = flt(
        opp.get("custom_win_probability")
    )
    amount = flt(
        opp.get("opportunity_amount")
    )

    revenue_estimate = amount * win_probability / 100
    health = _get_health(opp)

    timeline = _get_timeline(
        opp,
        handoffs,
        followups,
        emails,
        conversations
    )

    return {
        "opportunity": opp,
        "ai_lead": ai_lead,
        "health": health,
        "revenue_estimate": revenue_estimate,
        "handoffs": handoffs,
        "followups": followups,
        "emails": emails,
        "whatsapp_messages": whatsapp_messages,
        "timeline": timeline
    }


def _get_opportunity(opportunity):

    fields = _existing_fields(
        "Opportunity",
        [
            "name",
            "customer_name",
            "party_name",
            "opportunity_from",
            "opportunity_amount",
            "status",
            "source",
            "transaction_date",
            "expected_closing",
            "custom_pipeline_stage",
            "custom_win_probability",
            "custom_ai_deal_score",
            "custom_risk_level",
            "custom_next_best_action",
            "custom_ai_summary",
            "creation",
            "modified"
        ]
    )

    return frappe.db.get_value(
        "Opportunity",
        opportunity,
        fields,
        as_dict=True
    )


def _get_ai_lead(opp):

    if not _doctype_exists("AI Lead"):
        return {}

    fields = _existing_fields(
        "AI Lead",
        [
            "name",
            "lead_name",
            "email",
            "company",
            "contact",
            "source",
            "intent_type",
            "lead_category",
            "icp_score",
            "message",
            "custom_erp_lead",
            "custom_erp_opportunity",
            "creation"
        ]
    )

    filters = []

    if _has_field("AI Lead", "custom_erp_opportunity"):
        filters.append({
            "custom_erp_opportunity": opp.get("name")
        })

    if (
        opp.get("party_name")
        and _has_field("AI Lead", "custom_erp_lead")
    ):
        filters.append({
            "custom_erp_lead": opp.get("party_name")
        })

    for row_filter in filters:
        row = frappe.db.get_value(
            "AI Lead",
            row_filter,
            fields,
            as_dict=True
        )

        if row:
            return row

    return {}


def _get_handoffs(opportunity):

    if not _doctype_exists("AI Handoff"):
        return []

    return frappe.get_all(
        "AI Handoff",
        filters={
            "opportunity": opportunity
        },
        fields=_existing_fields(
            "AI Handoff",
            [
                "name",
                "assigned_to",
                "status",
                "priority",
                "followup_count",
                "last_followup_at",
                "next_followup_due",
                "sla_status",
                "notes",
                "creation",
                "modified"
            ]
        ),
        order_by="modified desc",
        limit_page_length=10
    )


def _get_followups(opportunity):

    fields = _existing_fields(
        "ToDo",
        [
            "name",
            "description",
            "status",
            "priority",
            "allocated_to",
            "date",
            "creation",
            "modified"
        ]
    )

    return frappe.get_all(
        "ToDo",
        filters={
            "reference_type": "Opportunity",
            "reference_name": opportunity
        },
        fields=fields,
        order_by="modified desc",
        limit_page_length=20
    )


def _get_emails(opportunity, ai_lead):

    if not _doctype_exists("Communication"):
        return []

    fields = _existing_fields(
        "Communication",
        [
            "name",
            "communication_type",
            "communication_medium",
            "sent_or_received",
            "subject",
            "content",
            "sender",
            "recipients",
            "creation"
        ]
    )

    rows = []

    if (
        _has_field("Communication", "reference_doctype")
        and _has_field("Communication", "reference_name")
    ):
        rows.extend(
            frappe.get_all(
                "Communication",
                filters={
                    "reference_doctype": "Opportunity",
                    "reference_name": opportunity
                },
                fields=fields,
                order_by="creation desc",
                limit_page_length=10
            )
        )

    email = ai_lead.get("email") if ai_lead else None

    if email and _has_field("Communication", "sender"):
        rows.extend(
            frappe.get_all(
                "Communication",
                filters={
                    "sender": ["like", f"%{email}%"]
                },
                fields=fields,
                order_by="creation desc",
                limit_page_length=10
            )
        )

    return _unique_rows(rows)[:10]


def _get_conversations(ai_lead):

    if not ai_lead or not _doctype_exists("CRM Conversation"):
        return []

    filters = None

    if (
        ai_lead.get("name")
        and _has_field("CRM Conversation", "custom_ai_lead")
    ):
        filters = {
            "custom_ai_lead": ai_lead.get("name")
        }

    elif (
        ai_lead.get("contact")
        and _has_field("CRM Conversation", "contact")
    ):
        filters = {
            "contact": ai_lead.get("contact")
        }

    if not filters:
        return []

    return frappe.get_all(
        "CRM Conversation",
        filters=filters,
        fields=_existing_fields(
            "CRM Conversation",
            [
                "name",
                "channel",
                "direction",
                "message",
                "ai_reply",
                "intent",
                "timestamp",
                "creation"
            ]
        ),
        order_by="timestamp desc",
        limit_page_length=20
    )


def _get_timeline(
    opp,
    handoffs,
    followups,
    emails,
    conversations
):

    timeline = [{
        "type": "Opportunity",
        "title": "Opportunity Created",
        "description": opp.get("name"),
        "timestamp": opp.get("creation")
    }]

    for row in handoffs:
        timeline.append({
            "type": "Handoff",
            "title": "Sales Handoff",
            "description": (
                f"{row.get('assigned_to') or ''} "
                f"({row.get('status') or ''})"
            ).strip(),
            "timestamp": row.get("creation")
        })

    for row in followups:
        timeline.append({
            "type": "Followup",
            "title": row.get("description") or "Follow-up",
            "description": row.get("status"),
            "timestamp": row.get("date") or row.get("creation")
        })

    for row in emails:
        timeline.append({
            "type": "Email",
            "title": row.get("subject") or "Email",
            "description": row.get("sent_or_received"),
            "timestamp": row.get("creation")
        })

    for row in conversations:
        timeline.append({
            "type": row.get("channel") or "Conversation",
            "title": row.get("direction") or "Conversation",
            "description": row.get("message"),
            "timestamp": row.get("timestamp") or row.get("creation")
        })

    timeline.sort(
        key=lambda row: _timeline_sort_key(
            row.get("timestamp")
        ),
        reverse=True
    )

    return timeline[:25]


def _timeline_sort_key(value):

    if not value:
        return ""

    if hasattr(value, "isoformat"):
        return value.isoformat()

    return str(value)


def _get_health(opp):

    risk = (
        opp.get("custom_risk_level")
        or ""
    ).lower()

    probability = flt(
        opp.get("custom_win_probability")
    )

    if risk == "high" or probability < 40:
        return "At Risk"

    if risk == "medium" or probability < 70:
        return "Moderate"

    return "Healthy"


def _doctype_exists(doctype):

    return bool(
        frappe.db.exists(
            "DocType",
            doctype
        )
    )


def _has_field(doctype, fieldname):

    if fieldname in SYSTEM_FIELDS:
        return True

    try:
        return bool(
            frappe.get_meta(doctype).has_field(fieldname)
        )
    except Exception:
        return False


def _existing_fields(doctype, fields):

    return [
        field
        for field in fields
        if _has_field(doctype, field)
    ]


def _unique_rows(rows):

    seen = set()
    unique = []

    for row in rows:
        key = row.get("name")

        if key and key in seen:
            continue

        if key:
            seen.add(key)

        unique.append(row)

    return unique
