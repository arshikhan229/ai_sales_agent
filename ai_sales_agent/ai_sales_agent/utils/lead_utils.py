import frappe

from ai_sales_agent.ai_sales_agent.utils.erpnext_crm_sync import (
    sync_hot_lead_to_crm
)


def find_duplicate_lead(
    email=None,
    phone=None,
    facebook_id=None,
    source=None,
    lead_name=None,
    contact=None
):
    """
    Duplicate detection priority:

    Contact
    Email
    Phone
    Facebook ID
    Source + Lead Name
    """

    # =================================
    # CONTACT MATCH
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
    # PHONE MATCH
    # =================================

    if phone:

        existing = frappe.db.exists(
            "AI Lead",
            {
                "custom_phone": phone
            }
        )

        if existing:
            return existing

    # =================================
    # FACEBOOK MATCH
    # =================================

    if facebook_id:

        existing = frappe.db.exists(
            "AI Lead",
            {
                "custom_facebook_id": facebook_id
            }
        )

        if existing:
            return existing

    # =================================
    # SOURCE + LEAD NAME
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
    phone=None,
    facebook_id=None,
    company=None,
    contact=None
):
    """
    Create or update AI Lead.
    """

    existing = find_duplicate_lead(
        email=email,
        phone=phone,
        facebook_id=facebook_id,
        source=source,
        lead_name=lead_name,
        contact=contact
    )

    if existing:

        lead = frappe.get_doc(
            "AI Lead",
            existing
        )

        if message:
            lead.message = message

        if email and not lead.email:
            lead.email = email

        if phone and not getattr(lead, "custom_phone", None):
            lead.custom_phone = phone

        if (
            facebook_id
            and not getattr(
                lead,
                "custom_facebook_id",
                None
            )
        ):
            lead.custom_facebook_id = facebook_id

        if company and not lead.company:
            lead.company = company

        if contact and not lead.contact:
            lead.contact = contact

        lead.flags.ignore_version = True

        lead.save(
            ignore_permissions=True
        )

        return lead

    # =================================
    # CREATE NEW LEAD
    # =================================

    lead = frappe.get_doc({
        "doctype": "AI Lead",
        "lead_name": lead_name,
        "email": email,
        "custom_phone": phone,
        "custom_facebook_id": facebook_id,
        "company": company,
        "contact": contact,
        "source": source,
        "message": message,
        "create_at": frappe.utils.now_datetime()
    })

    lead.insert(
        ignore_permissions=True
    )

    return lead


def update_ai_lead(
    lead,
    analysis
):
    """
    Update AI analysis and sync CRM.
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

    # =================================
    # CRM SYNC
    # =================================

    if lead.lead_category in [
        "Warm",
        "Hot"
    ]:

        crm_result = sync_hot_lead_to_crm(
            lead
        )

        if crm_result:

            lead.custom_erp_lead = crm_result.get(
                "erp_lead"
            )

            lead.custom_erp_opportunity = crm_result.get(
                "erp_opportunity"
            )

            lead.custom_last_crm_sync = (
                frappe.utils.now_datetime()
            )

            lead.flags.ignore_version = True

            lead.save(
                ignore_permissions=True
            )

            return lead