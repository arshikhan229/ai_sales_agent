import frappe

from ai_sales_agent.ai_sales_agent.utils.ai_engine import (
    analyze_lead
)

from ai_sales_agent.ai_sales_agent.utils.reply_engine import (
    generate_ai_reply
)

from ai_sales_agent.ai_sales_agent.whatsapp.whatsapp_sender import (
    send_whatsapp_message
)

from ai_sales_agent.ai_sales_agent.utils.conversation_logger import (
    log_conversation
)

from ai_sales_agent.ai_sales_agent.utils.lead_utils import (
    create_ai_lead,
    update_ai_lead
)



@frappe.whitelist(allow_guest=True)
def whatsapp_webhook():

    try:

        data = frappe.form_dict

        customer_message = (
            data.get("Body")
            or ""
        )

        customer_number = (
            data.get("From")
            or ""
        )

        customer_number = (
            customer_number
            .replace("whatsapp:", "")
        )

        frappe.logger().info(
            f"WHATSAPP INCOMING => "
            f"{customer_number} : "
            f"{customer_message}"
        )

        contact_name = frappe.db.get_value(
            "Contact",
            {
                "mobile_no": customer_number
            }
        )

        if not contact_name:

            contact = frappe.get_doc({
                "doctype": "Contact",
                "first_name": customer_number,
                "mobile_no": customer_number
            })

            contact.insert(
                ignore_permissions=True
            )

            frappe.db.commit()

            contact_name = contact.name

        # ==========================
        # CREATE AI LEAD
        # ==========================

        lead = create_ai_lead(
            lead_name=customer_number,
            source="WhatsApp",
            message=customer_message
        )

        # ==========================
        # AI ANALYSIS
        # ==========================

        analysis = analyze_lead(
            message=customer_message,
            email=""
        )

        update_ai_lead(
            lead,
            analysis
        )
         
        intent = analysis.get(
            "intent_type"
        )

        lead_category = analysis.get(
            "lead_category"
        )

        # ==========================
        # AI REPLY
        # ==========================

        ai_reply = generate_ai_reply(
            message=customer_message,
            intent=intent,
            lead_category=lead_category,
            channel="WhatsApp"
        )

        # ==========================
        # SEND WHATSAPP
        # ==========================

        send_whatsapp_message(
            to_number=customer_number,
            message=ai_reply
        )

        # ==========================
        # LOG CONVERSATION
        # ==========================

        log_conversation(
            contact=contact_name,
            channel="WhatsApp",
            direction="Incoming",
            message=customer_message,
            ai_reply=ai_reply,
            intent=intent
        )

        frappe.logger().info(
            "WHATSAPP FLOW SUCCESS"
        )

        return "OK"

    except Exception:

        frappe.log_error(
            frappe.get_traceback(),
            "WHATSAPP WEBHOOK ERROR"
        )

        return "ERROR"