import frappe


@frappe.whitelist()
def get_inbox():

    contacts = frappe.db.sql("""
        SELECT
            contact,
            COUNT(*) as total_messages,
            MAX(timestamp) as last_activity
        FROM `tabCRM Conversation`
        GROUP BY contact
        ORDER BY last_activity DESC
        LIMIT 200
    """, as_dict=True)

    results = []

    for row in contacts:

        latest = frappe.db.sql("""
            SELECT
                intent,
                message
            FROM `tabCRM Conversation`
            WHERE contact=%s
            ORDER BY timestamp DESC
            LIMIT 1
        """, (row.contact,), as_dict=True)

        latest = latest[0] if latest else {}

        intent = latest.get(
            "intent",
            ""
        )

        if intent == "General Inquiry":
            continue

        lead_category = ""
        icp_score = 0
        opportunity = ""

        # =====================================
        # DISPLAY CONTACT NAME
        # =====================================

        display_contact = row.contact

        if frappe.db.exists(
            "Contact",
            row.contact
        ):

            contact_doc = frappe.get_doc(
                "Contact",
                row.contact
            )

            if getattr(
                contact_doc,
                "custom_facebook_id",
                None
            ):
                display_contact = (
                    f"FB_{contact_doc.custom_facebook_id}"
                )

            elif contact_doc.first_name:
                display_contact = (
                    contact_doc.first_name
                )

        # =====================================
        # AI LEAD
        # =====================================

        ai_lead_name = frappe.db.get_value(
            "AI Lead",
            {
                "contact": row.contact
            },
            "name"
        )

        if ai_lead_name:

            ai_lead = frappe.get_doc(
                "AI Lead",
                ai_lead_name
            )

            lead_category = (
                ai_lead.lead_category
                or ""
            )

            icp_score = (
                ai_lead.icp_score
                or 0
            )

            # =================================
            # ERPNext Lead
            # =================================

            erp_lead = None

            if ai_lead.email:

                erp_lead = frappe.db.get_value(
                    "Lead",
                    {
                        "email_id": ai_lead.email
                    },
                    "name"
                )

            # =================================
            # Opportunity
            # =================================

            if erp_lead:

                opportunity = frappe.db.get_value(
                    "Opportunity",
                    {
                        "party_name": erp_lead
                    },
                    "name"
                ) or ""

        results.append({

            "contact":
                display_contact,

            "messages":
                row.total_messages,

            "intent":
                intent,

            "lead_category":
                lead_category,

            "icp_score":
                icp_score,

            "opportunity":
                opportunity,

            "last_activity":
                row.last_activity
        })

    return results


@frappe.whitelist()
def get_contact_timeline(contact):

    # Handle FB_123456 format
    if contact.startswith("FB_"):

        fb_id = contact.replace(
            "FB_",
            ""
        )

        actual_contact = frappe.db.get_value(
            "Contact",
            {
                "custom_facebook_id": fb_id
            },
            "name"
        )

        if actual_contact:
            contact = actual_contact

    return frappe.get_all(
        "CRM Conversation",
        filters={
            "contact": contact
        },
        fields=[
            "name",
            "contact",
            "channel",
            "direction",
            "message",
            "ai_reply",
            "intent",
            "timestamp"
        ],
        order_by="timestamp asc"
    )