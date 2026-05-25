import frappe

from ai_sales_agent.integrations.twilio_sender import (
    send_whatsapp_message
)


@frappe.whitelist(allow_guest=True)
def create_ai_lead():

    from_number = frappe.form_dict.get("From")
    message_body = frappe.form_dict.get("Body")

    if not message_body:
        return {
            "status": "error",
            "message": "No message received"
        }

    lead = frappe.get_doc({
        "doctype": "AI Lead",
        "lead_name": from_number,
        "source": "WhatsApp",
        "message": message_body
    })

    lead.insert(ignore_permissions=True)
    frappe.db.commit()

    reply_message = f"""
Hello 👋

Thank you for contacting us.

Your inquiry has been received successfully.

Lead Category: {lead.lead_category}
Department: {lead.assigned_department}

Our team will contact you shortly.
"""

    send_whatsapp_message(
        to_number=from_number.replace("whatsapp:", ""),
        message=reply_message
    )

    return {
        "status": "success",
        "lead": lead.name
    }