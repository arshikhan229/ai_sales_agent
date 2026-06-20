import frappe


@frappe.whitelist()
def get_handoffs():

    return frappe.get_all(
        "AI Handoff",
        fields=[
            "name",
            "lead",
            "assigned_to",
            "status",
            "priority",
            "opportunity",
            "followup_count",
            "sla_status",
            "next_best_action"
        ],
        order_by="modified desc",
        limit=500
    )


@frappe.whitelist()
def reassign_handoff(handoff, user):

    doc = frappe.get_doc(
        "AI Handoff",
        handoff
    )

    doc.assigned_to = user

    doc.save(
        ignore_permissions=True
    )

    frappe.db.commit()

    return {
        "success": True
    }