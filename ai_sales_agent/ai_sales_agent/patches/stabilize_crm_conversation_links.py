import frappe


def execute():
    if not frappe.db.table_exists("CRM Conversation"):
        return

    if not frappe.db.table_exists("AI Lead"):
        return

    if not frappe.db.has_column("CRM Conversation", "custom_ai_lead"):
        return

    conversations = frappe.db.sql(
        """
        SELECT name, contact
        FROM `tabCRM Conversation`
        WHERE contact IS NOT NULL
            AND contact != ''
            AND IFNULL(custom_ai_lead, '') = ''
        LIMIT 10000
        """,
        as_dict=True,
    )

    updated = 0

    for row in conversations:
        ai_lead = frappe.db.get_value(
            "AI Lead",
            {"contact": row.contact},
            ["name", "email", "lead_name"],
            as_dict=True,
        )

        if not ai_lead:
            continue

        values = {"custom_ai_lead": ai_lead.name}

        erp_lead = _find_erp_lead(ai_lead)
        if erp_lead and frappe.db.has_column("CRM Conversation", "custom_erp_lead"):
            values["custom_erp_lead"] = erp_lead

        frappe.db.set_value(
            "CRM Conversation",
            row.name,
            values,
            update_modified=False,
        )
        updated += 1

    frappe.db.commit()
    frappe.logger().info(
        f"stabilize_crm_conversation_links updated={updated}"
    )


def _find_erp_lead(ai_lead):
    if ai_lead.email:
        erp_lead = frappe.db.get_value(
            "Lead",
            {"email_id": ai_lead.email},
            "name",
        )
        if erp_lead:
            return erp_lead

    if ai_lead.lead_name:
        return frappe.db.get_value(
            "Lead",
            {"lead_name": ai_lead.lead_name},
            "name",
        )

    return None
