import frappe

from ai_sales_agent.ai_sales_agent.utils.erpnext_crm_sync import (
    create_erpnext_lead
)
from ai_sales_agent.ai_sales_agent.utils.erpnext_crm_sync import (
    sync_hot_lead_to_crm
)


def find_duplicate_lead(
    email=None,
    source=None,
    lead_name=None
):
    """
    Check if AI Lead already exists
    """

    if email:

        existing = frappe.db.exists(
            "AI Lead",
            {
                "email": email
            }
        )

        if existing:
            return existing

    if source and lead_name:

        existing = frappe.db.exists(
            "AI Lead",
            {
                "source": source,
                "lead_name": lead_name
            }
        )

        if existing:
            return existing

    return None


def create_ai_lead(
    lead_name,
    source,
    message,
    email=None,
    company=None
):
    """
    Create AI Lead if not exists
    """

    existing = find_duplicate_lead(
        email=email,
        source=source,
        lead_name=lead_name
    )

    if existing:

        return frappe.get_doc(
            "AI Lead",
            existing
        )

    lead = frappe.get_doc({

        "doctype": "AI Lead",

        "lead_name": lead_name,

        "email": email,

        "company": company,

        "source": source,

        "message": message,

        "create_at":
            frappe.utils.now_datetime()

    })

    lead.insert(
        ignore_permissions=True
    )

    frappe.db.commit()

    return lead


def update_ai_lead(
    lead,
    analysis
):
    """
    Update AI Lead with AI analysis
    """

    lead.intent_type = (
        analysis.get(
            "intent_type"
        )
    )

    lead.intent_confidence = (
        analysis.get(
            "intent_confidence"
        )
    )

    lead.icp_score = (
        analysis.get(
            "icp_score"
        )
    )

    lead.lead_category = (
        analysis.get(
            "lead_category"
        )
    )

    lead.ai_reason = (
        analysis.get(
            "reason"
        )
    )

    lead.processed_at = (
        frappe.utils.now_datetime()
    )

    lead.flags.ignore_version = True

    lead.save(
        ignore_permissions=True
    )

    frappe.db.commit()

    # ==========================
    # ERPNext CRM Sync
    # ==========================

    if (
        lead.lead_category == "Hot"
        or
        (lead.icp_score or 0) >= 40
    ):

        sync_hot_lead_to_crm(
            lead
        )

    return lead