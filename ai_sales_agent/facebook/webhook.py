import frappe
from werkzeug.wrappers import Response

from ai_sales_agent.ai_sales_agent.utils.ai_engine import (
    analyze_lead
)

from ai_sales_agent.ai_sales_agent.utils.reply_engine import (
    generate_ai_reply
)

from ai_sales_agent.ai_sales_agent.utils.contact_matcher import (
    find_or_create_contact
)

from ai_sales_agent.ai_sales_agent.utils.lead_utils import (
    create_ai_lead,
    update_ai_lead
)

from ai_sales_agent.facebook.facebook_sender import (
    send_facebook_message
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

                    # ==================================
                    # CONTACT MATCHING
                    # ==================================

                    contact = find_or_create_contact(
                        facebook_id=sender_id
                    )

                    frappe.logger().info(
                        f"CONTACT FOUND => {contact.name}"
                    )

                    # ==================================
                    # CREATE / REUSE AI LEAD
                    # ==================================

                    lead = create_ai_lead(
                        lead_name=sender_id or "Facebook User",
                        source="Facebook",
                        message=message_text,
                        company=getattr(
                            contact,
                            "company_name",
                            None
                        )
                    )

                    # ==================================
                    # AI ANALYSIS
                    # ==================================

                    analysis = analyze_lead(
                        message=message_text,
                        email=None,
                        company=getattr(
                            contact,
                            "company_name",
                            None
                        )
                    )

                    # ==================================
                    # UPDATE AI LEAD
                    # ==================================

                    update_ai_lead(
                        lead,
                        analysis
                    )

                    # ==================================
                    # UPDATE ERPNext CONTACT
                    # ==================================

                    contact.custom_lead_score = (
                        analysis.get(
                            "icp_score"
                        )
                    )

                    contact.custom_lead_category = (
                        analysis.get(
                            "lead_category"
                        )
                    )

                    contact.save(
                        ignore_permissions=True
                    )

                    frappe.db.commit()

                    # ==================================
                    # GENERATE AI REPLY
                    # ==================================

                    try:

                        reply = generate_ai_reply(
                            message=message_text,

                            intent=analysis.get(
                                "intent_type"
                            ),

                            lead_category=analysis.get(
                                "lead_category"
                            ),

                            company=getattr(
                                contact,
                                "company_name",
                                None
                            ),

                            channel="Facebook"
                        )

                        # ==================================
                        # SEND FACEBOOK MESSAGE
                        # ==================================

                        send_facebook_message(
                            recipient_id=sender_id,
                            message=reply
                        )

                        frappe.logger().info(
                            f"FACEBOOK REPLY SENT => "
                            f"{sender_id}"
                        )

                    except Exception:

                        frappe.log_error(
                            frappe.get_traceback(),
                            "FACEBOOK AUTO REPLY ERROR"
                        )

                    frappe.logger().info(
                        f"AI LEAD UPDATED => "
                        f"{lead.name}"
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