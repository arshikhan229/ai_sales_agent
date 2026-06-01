import frappe


def log_conversation(
    contact,
    channel,
    direction,
    message,
    ai_reply=None,
    intent=None
):
    """
    Save conversation into CRM Conversation
    """

    try:

        if not contact:
            return None

        doc = frappe.get_doc({
            "doctype": "CRM Conversation",
            "contact": contact,
            "channel": channel,
            "direction": direction,
            "message": message,
            "ai_reply": ai_reply,
            "intent": intent,
            "timestamp": frappe.utils.now()
        })

        doc.insert(
            ignore_permissions=True
        )

        frappe.db.commit()

        return doc

    except Exception:

        frappe.log_error(
            frappe.get_traceback(),
            "CRM CONVERSATION LOGGER ERROR"
        )

        return None