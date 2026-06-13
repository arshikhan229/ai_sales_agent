import os
import frappe

def _resolve_phone(contact):
    """Resolve a phone number string from a Contact name or raw phone string."""
    try:
        # If it's a Contact doc name, fetch phone/mobile
        if isinstance(contact, str) and contact and frappe.db.exists("Contact", contact):
            c = frappe.get_doc("Contact", contact)
            for fld in ("mobile_no", "phone", "phone_number"):
                val = getattr(c, fld, None)
                if val:
                    return val
            return None

        # otherwise assume it's already a phone number
        return contact
    except Exception:
        frappe.log_error(frappe.get_traceback(), "whatsapp_sender_resolve_phone_error")
        return None


def send_whatsapp(contact, message):
    """Send a WhatsApp message using Twilio's API.

    Config (in site_config or env):
      - twilio_account_sid
      - twilio_auth_token
      - twilio_whatsapp_from  (E.164 number, e.g. +1415xxxx)
    """
    try:
        to = _resolve_phone(contact)
        if not to:
            frappe.logger().info("whatsapp_sender: no recipient phone found for %s" % str(contact))
            return False

        sid = frappe.conf.get("twilio_account_sid") or os.getenv("TWILIO_ACCOUNT_SID")
        token = frappe.conf.get("twilio_auth_token") or os.getenv("TWILIO_AUTH_TOKEN")
        from_no = frappe.conf.get("twilio_whatsapp_from") or os.getenv("TWILIO_WHATSAPP_FROM")

        if not (sid and token and from_no):
            frappe.logger().info("whatsapp_sender: Twilio config missing; check site_config.json or env vars")
            return False

        try:
            import requests
        except Exception:
            frappe.log_error(frappe.get_traceback(), "whatsapp_sender_missing_requests")
            return False

        url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"
        data = {
            "From": f"whatsapp:{from_no}",
            "To": f"whatsapp:{to}",
            "Body": message,
        }

        resp = requests.post(url, data=data, auth=(sid, token), timeout=15)
        if resp.status_code in (200, 201):
            return True
        else:
            frappe.log_error(f"whatsapp_sender_failed: {resp.status_code} {resp.text}", "whatsapp_sender_error")
            return False

    except Exception:
        frappe.log_error(frappe.get_traceback(), "whatsapp_sender_exception")
        return False
