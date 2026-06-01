import frappe

from twilio.rest import Client


def send_whatsapp_message(
    to_number,
    message
):
    """
    Send WhatsApp message using Twilio
    """

    try:

        settings = frappe.get_single(
            "AI Settings"
        )

        account_sid = (
            settings.twilio_sid
        )

        auth_token = settings.get_password(
            "twilio_token"
        )

        from_number = (
            settings.twilio_whatsapp_number
        )

        if not account_sid:
            frappe.throw(
                "Twilio SID missing"
            )

        if not auth_token:
            frappe.throw(
                "Twilio Token missing"
            )

        if not from_number:
            frappe.throw(
                "Twilio WhatsApp Number missing"
            )

        client = Client(
            account_sid,
            auth_token
        )

        response = client.messages.create(
            body=message,

            from_=f"whatsapp:{from_number}",

            to=f"whatsapp:{to_number}"
        )

        frappe.logger().info(
            f"WhatsApp sent => {response.sid}"
        )

        return response.sid

    except Exception:

        frappe.log_error(
            frappe.get_traceback(),
            "WHATSAPP SENDER ERROR"
        )

        return None