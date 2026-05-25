import requests
import frappe


def send_facebook_message(recipient_id, message):

    settings = frappe.get_single("AI Settings")

    page_access_token = settings.get_password(
        "facebook_page_access_token"
    )

    url = (
        "https://graph.facebook.com/v25.0/me/messages"
    )

    payload = {
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message
        }
    }

    params = {
        "access_token": page_access_token
    }

    response = requests.post(
        url,
        params=params,
        json=payload,
        timeout=20
    )

    frappe.logger().info(
        f"FB SEND RESPONSE => {response.text}"
    )

    return response.json()