import frappe
from werkzeug.wrappers import Response

from ai_sales_agent.ai_sales_agent.utils.channel_processor import (
    process_inbound_message,
)


@frappe.whitelist(allow_guest=True)
def facebook_webhook():

    # ==================================================
    # FACEBOOK WEBHOOK VERIFICATION
    # ==================================================
    if frappe.request.method == "GET":

        try:

            settings = frappe.get_single(
                "AI Settings"
            )

            hub_mode = frappe.form_dict.get(
                "hub.mode"
            )

            hub_token = frappe.form_dict.get(
                "hub.verify_token"
            )

            hub_challenge = frappe.form_dict.get(
                "hub.challenge"
            )

            if (
                hub_mode == "subscribe"
                and hub_token
                == settings.facebook_verify_token
            ):

                return Response(
                    response=str(hub_challenge),
                    status=200,
                    content_type="text/plain"
                )

            return Response(
                response="Verification failed",
                status=403
            )

        except Exception:

            frappe.log_error(
                frappe.get_traceback(),
                "FACEBOOK VERIFY ERROR"
            )

            return Response(
                response="Verification failed",
                status=403
            )

    # ==================================================
    # FACEBOOK MESSAGE EVENTS
    # ==================================================
    if frappe.request.method == "POST":

        try:

            data = frappe.request.get_json()

            frappe.log_error(
                title="FACEBOOK RAW PAYLOAD",
                message=frappe.as_json(data)
            )

            if not data:

                return Response(
                    response="NO DATA",
                    status=200
                )

            if data.get("object") != "page":

                return Response(
                    response="IGNORED",
                    status=200
                )

            for entry in data.get("entry", []):

                for event in entry.get(
                    "messaging",
                    []
                ):

                    sender_id = (
                        event.get(
                            "sender",
                            {}
                        ).get("id")
                    )

                    message_text = (
                        event.get(
                            "message",
                            {}
                        ).get("text")
                    )

                    if not message_text:
                        continue

                    result = process_inbound_message(
                        channel="Facebook",
                        message=message_text,
                        facebook_id=sender_id,
                        reply_target={
                            "facebook_id": sender_id,
                        },
                    )

                    if (
                        not result.get("success")
                        and not result.get("skipped")
                    ):

                        frappe.log_error(
                            frappe.as_json(result),
                            "FACEBOOK PROCESSOR FAILED",
                        )

            return Response(
                response="EVENT_RECEIVED",
                status=200
            )

        except Exception:

            frappe.log_error(
                frappe.get_traceback(),
                "FACEBOOK WEBHOOK ERROR"
            )

            return Response(
                response="ERROR",
                status=200
            )

    return Response(
        response="OK",
        status=200
    )
