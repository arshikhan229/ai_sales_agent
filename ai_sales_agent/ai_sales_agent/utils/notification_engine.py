import frappe


def create_notification(title, message):
    """
    Create system notification
    """

    frappe.get_doc({
        "doctype": "Notification Log",
        "subject": title,
        "email_content": message,
        "for_user": "Administrator",
        "type": "Alert"
    }).insert(ignore_permissions=True)