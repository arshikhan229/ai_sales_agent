import os
import frappe

def _resolve_recipient(contact):
    """Resolve Facebook recipient id from a Contact doc or raw id."""
    try:
        if isinstance(contact, str) and contact and frappe.db.exists("Contact", contact):
            c = frappe.get_doc("Contact", contact)
            # common field where messenger ids are stored
            for fld in ("facebook_messenger_id", "fb_psid", "messenger_id"):
                val = getattr(c, fld, None)
                if val:
                    return val
            return None

        return contact
    except Exception:
        frappe.log_error(frappe.get_traceback(), "facebook_sender_resolve_error")
        return None


def send_facebook(contact, message):
    """Send a Facebook Messenger message using the Graph API.

    Config (in site_config or env):
      - facebook_page_access_token
    """
    try:
        recipient = _resolve_recipient(contact)
        if not recipient:
            frappe.logger().info("facebook_sender: no recipient id found for %s" % str(contact))
            return False

        token = frappe.conf.get("facebook_page_access_token") or os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")
        if not token:
            frappe.logger().info("facebook_sender: page access token missing in site_config or env")
            return False

        try:
            import requests
        except Exception:
            frappe.log_error(frappe.get_traceback(), "facebook_sender_missing_requests")
            return False

        url = f"https://graph.facebook.com/v16.0/me/messages?access_token={token}"
        payload = {
            "recipient": {"id": recipient},
            "message": {"text": message}
        }

        resp = requests.post(url, json=payload, timeout=15)
        if resp.status_code in (200, 201):
            return True
        else:
            frappe.log_error(f"facebook_sender_failed: {resp.status_code} {resp.text}", "facebook_sender_error")
            return False

    except Exception:
        frappe.log_error(frappe.get_traceback(), "facebook_sender_exception")
        return False
