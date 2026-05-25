import frappe
from werkzeug.wrappers import Response

from ai_sales_agent.ai_sales_agent.utils.ai_engine import (
    analyze_lead
)

from ai_sales_agent.ai_sales_agent.utils.reply_engine import (
    generate_ai_reply
)

from ai_sales_agent.facebook.facebook_sender import (
    send_facebook_message
)


@frappe.whitelist(allow_guest=True)
def facebook_webhook():

    # ==========================================
    # FACEBOOK WEBHOOK VERIFICATION
    # ==========================================
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
                and hub_token ==
                settings.facebook_verify_token
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

    # ==========================================
    # FACEBOOK EVENTS
    # ==========================================
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

                    # Ignore empty events
                    if not message_text:
                        continue

                    # ==================================
                    # CREATE AI LEAD
                    # ==================================
                    lead = frappe.get_doc({
                        "doctype": "AI Lead",
                        "lead_name":
                            sender_id
                            or "Facebook User",
                        "source": "Facebook",
                        "message": message_text,
                        "create_at":
                            frappe.utils.now_datetime()
                    })

                    lead.insert(
                        ignore_permissions=True
                    )

                    frappe.db.commit()

                    # ==================================
                    # AI ANALYSIS
                    # ==================================
                    analysis = analyze_lead(
                        message=message_text,
                        email=getattr(
                            lead,
                            "email",
                            None
                        ),
                        company=getattr(
                            lead,
                            "company",
                            None
                        )
                    )

                    lead.intent_type = (
                        analysis.get(
                            "intent_type"
                        )
                    )

                    lead.intent_confidence = (
                        analysis.get(
                            "intent_confidence"
                        )
                    )

                    lead.icp_score = (
                        analysis.get(
                            "icp_score"
                        )
                    )

                    lead.lead_category = (
                        analysis.get(
                            "lead_category"
                        )
                    )

                    lead.ai_reason = (
                        analysis.get(
                            "reason"
                        )
                    )

                    lead.processed_at = (
                        frappe.utils.now_datetime()
                    )

                    lead.save(
                        ignore_permissions=True
                    )

                    frappe.db.commit()

                    # ==================================
                    # AI AUTO REPLY
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
                                lead,
                                "company",
                                None
                            )
                        )

                        send_facebook_message(
                            recipient_id=sender_id,
                            message=reply
                        )

                        frappe.logger().info(
                            f"AUTO REPLY SENT => "
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