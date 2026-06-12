import frappe


@frappe.whitelist()
def claim_handoff(handoff_name):
    """Assign the AI Handoff to the current user and reassign linked ToDo records.

    Args:
        handoff_name (str): name of the AI Handoff doc

    Returns:
        dict: {status: 'success'|'error', message: str, handoff_name, handoff_status, assigned_to}
    """
    try:
        if not handoff_name:
            return {"status": "error", "message": "handoff_name is required"}

        handoff = frappe.get_doc("AI Handoff", handoff_name)
        user = frappe.session.user

        handoff.assigned_to = user
        if (handoff.status or "").strip().lower() == "open":
            handoff.status = "Assigned"

        handoff.save(ignore_permissions=True)

        # Reassign linked ToDo records
        todos = frappe.get_all(
            "ToDo",
            filters={"reference_type": "AI Handoff", "reference_name": handoff.name},
            fields=["name"],
        )
        for t in todos:
            try:
                td = frappe.get_doc("ToDo", t.name)
                td.allocated_to = user
                td.save(ignore_permissions=True)
            except Exception:
                frappe.log_error(frappe.get_traceback(), "claim_handoff:todo_update_error")

        frappe.db.commit()

        return {
            "status": "success",
            "message": "Handoff claimed",
            "handoff_name": handoff.name,
            "handoff_status": handoff.status,
            "assigned_to": user,
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "claim_handoff_error")
        return {"status": "error", "message": str(e)}
