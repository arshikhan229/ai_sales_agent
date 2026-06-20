import base64
import hashlib
import hmac

import frappe


def validate_twilio_request(request=None):
    request = request or frappe.request
    signature = _get_header(request, "X-Twilio-Signature")

    if not signature:
        return False

    token = _get_ai_settings_password("twilio_token")
    if not token:
        return False

    url = getattr(request, "url", "") or ""

    if url.startswith("http://"):
        url = url.replace("http://", "https://", 1)
    form = getattr(request, "form", None) or {}
    payload = url + "".join(
        f"{key}{form.get(key)}"
        for key in sorted(form.keys())
    )

    digest = hmac.new(
        token.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha1,
    ).digest()

    expected = base64.b64encode(
        digest
    ).decode("ascii")

    frappe.log_error(
        f"""
    URL={url}

    SIGNATURE={signature}

    EXPECTED={expected}

    FORM={dict(form)}
    """,
        "TWILIO DEBUG"
    )

    return hmac.compare_digest(
        signature,
        expected
    )


def validate_facebook_request(request=None):
    request = request or frappe.request
    signature = _get_header(
        request,
        "X-Hub-Signature-256",
    )

    if not signature or not signature.startswith("sha256="):
        return False

    secret = _get_ai_settings_password("facebook_app_secret")
    if not secret:
        return False

    body = request.get_data() or b""
    expected = "sha256=" + hmac.new(
        secret.encode("utf-8"),
        body,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(signature, expected)


def _get_ai_settings_password(fieldname):
    try:
        settings = frappe.get_single("AI Settings")
        return settings.get_password(fieldname) or ""
    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            "webhook_security_settings_error",
        )
        return ""


def _get_header(request, key):
    headers = getattr(request, "headers", {}) or {}
    return headers.get(key) or headers.get(key.lower()) or ""
