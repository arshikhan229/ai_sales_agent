import frappe

from ai_sales_agent.ai_sales_agent.utils.erpnext_crm_sync import (
    sync_hot_lead_to_crm
)


def find_duplicate_lead(
    email=None,
    source=None,
    lead_name=None,
    contact=None
):
    """
    Universal duplicate detection
    for Email, Facebook, WhatsApp,
    Instagram and LinkedIn.
    """

    # =================================
    # CONTACT MATCH (BEST MATCH)
    # =================================

    if contact:

        existing = frappe.db.exists(
            "AI Lead",
            {
                "contact": contact
            }
        )

        if existing:
            return existing

    # =================================
    # EMAIL MATCH
    # =================================

    if email:

        existing = frappe.db.exists(
            "AI Lead",
            {
                "email": email
            }
        )

        if existing:
            return existing

    # =================================
    # SOURCE + LEAD NAME MATCH
    # =================================

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
    company=None,
    contact=None
):
    """
    Create AI Lead if not exists.
    Always update latest message.
    """

    existing = find_duplicate_lead(
        email=email,
        source=source,
        lead_name=lead_name,
        contact=contact
    )

    if existing:

        lead = frappe.get_doc(
            "AI Lead",
            existing
        )

        # Update latest message
        if message:
            lead.message = message

        # Update email if missing
        if email and not lead.email:
            lead.email = email

        # Update company if missing
        if company and not lead.company:
            lead.company = company

        # Update contact if missing
        if contact and not lead.contact:
            lead.contact = contact

        lead.save(
            ignore_permissions=True
        )

        frappe.db.commit()

        return lead

    # =================================
    # CREATE NEW AI LEAD
    # =================================

    lead = frappe.get_doc({

        "doctype": "AI Lead",

        "lead_name":
            lead_name,

        "email":
            email,

        "company":
            company,

        "contact":
            contact,

        "source":
            source,

        "message":
            message,

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

    # =================================
    # CRM SYNC
    # =================================

    if lead.lead_category in [
        "Warm",
        "Hot"
    ]:

        sync_hot_lead_to_crm(
            lead
        )

    return lead