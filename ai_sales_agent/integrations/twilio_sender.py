from twilio.rest import Client
import frappe


def send_whatsapp_message(to_number, message):
    """
    Send WhatsApp message using Twilio
    """

    try:
        settings = frappe.get_single("AI Settings")

        account_sid = settings.get_password("twilio_sid")
        auth_token = settings.get_password("twilio_token")

        client = Client(account_sid, auth_token)

        response = client.messages.create(
            body=message,
            from_='whatsapp:+14155238886',   # Twilio Sandbox Number
            to=f'whatsapp:{to_number}'
        )

        return response.sid

    except Exception as e:

        frappe.log_error(
            frappe.get_traceback(),
            "Twilio WhatsApp Error"
        )

        return None