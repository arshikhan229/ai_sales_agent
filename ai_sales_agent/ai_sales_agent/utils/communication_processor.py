import frappe

from ai_sales_agent.ai_sales_agent.utils.ai_engine import (
    analyze_lead
)

from ai_sales_agent.ai_sales_agent.utils.reply_engine import (
    generate_ai_reply
)

from ai_sales_agent.ai_sales_agent.utils.contact_matcher import (
    find_or_create_contact
)

from ai_sales_agent.ai_sales_agent.utils.conversation_logger import (
    log_conversation
)

from ai_sales_agent.ai_sales_agent.utils.context_builder import (
    build_customer_context
)

from ai_sales_agent.ai_sales_agent.utils.lead_utils import (
    create_ai_lead,
    update_ai_lead
)


def process_communication(doc, method=None):
    """
    Process incoming email communication
    """

    try:

        # Prevent recursion
        if getattr(doc, "_ai_processed", False):
            return

        # =================================
        # EXTRACT EMAIL CONTENT
        # =================================

        content = (
            doc.text_content
            or doc.content
            or doc.subject
            or ""
        )

        sender = (
            doc.sender
            or ""
        )

        if not content:
            return

        # =================================
        # FIND OR CREATE CONTACT
        # =================================

        contact = find_or_create_contact(
            email=sender
        )

        # =================================
        # CREATE / REUSE AI LEAD
        # =================================

        lead = create_ai_lead(
            lead_name=contact.name,
            source="Email",
            message=content,
            email=sender
        )

        # =================================
        # BUILD AI MEMORY CONTEXT
        # =================================

        context = build_customer_context(
            contact.name
        )

        # =================================
        # AI ANALYSIS
        # =================================

        analysis = analyze_lead(
            message=content,
            email=sender
        )

        # =================================
        # UPDATE AI LEAD
        # =================================

        update_ai_lead(
            lead,
            analysis
        )

        frappe.logger().info(
            f"AI ANALYSIS => {analysis}"
        )

        # =================================
        # AI REPLY
        # =================================

        reply = generate_ai_reply(
            message=content,
            intent=analysis.get(
                "intent_type"
            ),
            lead_category=analysis.get(
                "lead_category"
            ),
            company=None,
            channel="Email",
            context=context
        )

        frappe.logger().info(
            f"AI REPLY => {reply}"
        )

        # =================================
        # SAVE CRM CONVERSATION
        # =================================

        log_conversation(
            contact=contact.name,
            channel="Email",
            direction="Incoming",
            message=content,
            ai_reply=reply,
            intent=analysis.get(
                "intent_type"
            )
        )

        # =================================
        # UPDATE COMMUNICATION
        # =================================

        doc.custom_ai_intent = (
            analysis.get(
                "intent_type"
            )
        )

        doc.custom_ai_confidence = (
            analysis.get(
                "intent_confidence"
            )
        )

        doc.custom_lead_score = (
            analysis.get(
                "icp_score"
            )
        )

        doc.custom_lead_category = (
            analysis.get(
                "lead_category"
            )
        )

        doc.custom_ai_suggested_reply = (
            reply
        )

        # =================================
        # UPDATE CONTACT INTELLIGENCE
        # =================================

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

        # =================================
        # SAVE COMMUNICATION
        # =================================

        doc._ai_processed = True

        doc.save(
            ignore_permissions=True
        )

        frappe.db.commit()

        frappe.logger().info(
            f"AI Communication Processed => {doc.name}"
        )

    except Exception:

        frappe.log_error(
            frappe.get_traceback(),
            "COMMUNICATION PROCESSOR ERROR"
        )