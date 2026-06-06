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

from ai_sales_agent.ai_sales_agent.utils.contact_matcher import (
    find_or_create_contact
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
            .replace(" ", "")
            .strip()
        )

        if customer_number and not customer_number.startswith("+"):
            customer_number = f"+{customer_number}"

        frappe.logger().info(
            f"WHATSAPP INCOMING => {customer_number} : {customer_message}"
        )

        if not customer_number:

            frappe.log_error(
                "EMPTY CUSTOMER NUMBER",
                "WHATSAPP ERROR"
            )

            return "OK"

        # =====================================
        # CONTACT
        # =====================================

        contact = find_or_create_contact(
            phone=customer_number
        )

        contact_name = contact.name

        # =====================================
        # AI LEAD
        # =====================================

        lead = create_ai_lead(
            lead_name=customer_number,
            source="WhatsApp",
            message=customer_message,
            contact=contact_name
        )

        # =====================================
        # AI ANALYSIS
        # =====================================

        analysis = analyze_lead(
            message=customer_message,
            email=""
        )

        update_ai_lead(
            lead,
            analysis
        )

        frappe.logger().info(
            f"WHATSAPP ANALYSIS => {analysis}"
        )

        intent = analysis.get(
            "intent_type"
        )

        lead_category = analysis.get(
            "lead_category"
        )

        # =====================================
        # AI REPLY
        # =====================================

        ai_reply = generate_ai_reply(
            message=customer_message,
            intent=intent,
            lead_category=lead_category,
            channel="WhatsApp"
        )

        # =====================================
        # SEND MESSAGE
        # =====================================

        send_whatsapp_message(
            to_number=customer_number,
            message=ai_reply
        )

        # =====================================
        # CRM CONVERSATION
        # =====================================

        conversation = log_conversation(
            contact=contact_name,
            channel="WhatsApp",
            direction="Incoming",
            message=customer_message,
            ai_reply=ai_reply,
            intent=intent
        )

        frappe.logger().info(
            f"WHATSAPP CONVERSATION => {conversation.name}"
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