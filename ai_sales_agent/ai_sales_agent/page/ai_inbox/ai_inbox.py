import frappe


@frappe.whitelist()
def get_inbox():

    contacts = frappe.db.sql("""
        SELECT
            contact,
            COUNT(*) as total_messages,
            MAX(timestamp) as last_activity
        FROM `tabCRM Conversation`
        GROUP BY contact
        ORDER BY last_activity DESC
        LIMIT 500
    """, as_dict=True)

    results = []

    for row in contacts:

        latest = frappe.db.sql("""
            SELECT
                intent,
                message,
                channel
            FROM `tabCRM Conversation`
            WHERE contact=%s
            ORDER BY timestamp DESC
            LIMIT 1
        """, (row.contact,), as_dict=True)

        latest = latest[0] if latest else {}

        intent = latest.get("intent", "")
        channel = latest.get("channel", "")

        message_preview = (latest.get("message") or "")[:80]

        # =====================================
        # HIDE GENERAL INQUIRIES
        # =====================================

        if intent == "General Inquiry":
            continue

        lead_category = ""
        icp_score = 0
        opportunity = ""

        # =====================================
        # CONTACT DISPLAY
        # =====================================

        display_contact = row.contact

        if frappe.db.exists("Contact", row.contact):

            contact_doc = frappe.get_doc(
                "Contact",
                row.contact
            )

            if getattr(
                contact_doc,
                "custom_facebook_id",
                None
            ):
                display_contact = (
                    f"FB_{contact_doc.custom_facebook_id}"
                )

            elif contact_doc.first_name:
                display_contact = (
                    contact_doc.first_name
                )

        # =====================================
        # CHANNEL DISPLAY
        # =====================================

        channel_display = channel

        if channel == "WhatsApp":
            channel_display = "💬 WhatsApp"

        elif channel == "Facebook":
            channel_display = "📘 Facebook"

        elif channel == "Email":
            channel_display = "📧 Email"

        # =====================================
        # AI LEAD LOOKUP
        # =====================================

        ai_lead_name = frappe.db.get_value(
            "AI Lead",
            {
                "contact": row.contact
            },
            "name"
        )

        if ai_lead_name:

            ai_lead = frappe.get_doc(
                "AI Lead",
                ai_lead_name
            )

            lead_category = (
                ai_lead.lead_category
                or ""
            )

            icp_score = (
                ai_lead.icp_score
                or 0
            )

            # =====================================
            # FILTER SPAM / NEWSLETTER EMAILS
            # =====================================

            email = (
                ai_lead.email or ""
            ).lower()

            blocked_domains = (
                "github.com",
                "linkedin.com",
                "substack.com",
                "coursera.org",
                "coursera.com",
                "medium.com",
                "coinmarketcap.com",
                "academia-mail.com",
                "economist.com",
                "foodpanda.pk",
                "temuemail.com",
                "skyscanner.com",
            )

            if any(
                domain in email
                for domain in blocked_domains
            ):
                continue

            # =====================================
            # HIDE COLD LEADS
            # =====================================

            if lead_category == "Cold":
                continue

            # =====================================
            # CATEGORY BADGE
            # =====================================

            if lead_category == "Hot":
                lead_category = "🔥 Hot"

            elif lead_category == "Warm":
                lead_category = "🟡 Warm"

            elif lead_category == "Cold":
                lead_category = "⚪ Cold"

            # =====================================
            # ERP LEAD LOOKUP
            # =====================================

            erp_lead = None

            if ai_lead.email:

                erp_lead = frappe.db.get_value(
                    "Lead",
                    {
                        "email_id": ai_lead.email
                    },
                    "name"
                )

            if (
                not erp_lead
                and ai_lead.lead_name
            ):

                erp_lead = frappe.db.get_value(
                    "Lead",
                    {
                        "lead_name":
                            ai_lead.lead_name
                    },
                    "name"
                )

            # =====================================
            # OPPORTUNITY LOOKUP
            # =====================================

            if erp_lead:

                opportunity = frappe.db.get_value(
                    "Opportunity",
                    {
                        "opportunity_from": "Lead",
                        "party_name": erp_lead
                    },
                    "name"
                ) or ""

        results.append({

            "contact":
                display_contact,

            "actual_contact":
                row.contact,

            "channel":
                channel_display,

            "messages":
                row.total_messages,

            "intent":
                intent,

            "preview":
                message_preview,

            "lead_category":
                lead_category,

            "icp_score":
                icp_score,

            "opportunity":
                opportunity,

            "last_activity":
                row.last_activity
        })

    # =====================================
    # HOT LEADS FIRST
    # =====================================

    def sort_weight(item):

        category = item.get(
            "lead_category",
            ""
        )

        if "Hot" in category:
            priority = 3

        elif "Warm" in category:
            priority = 2

        else:
            priority = 1

        return (
            priority,
            item.get("icp_score", 0),
            item.get("last_activity")
        )

    results.sort(
        key=sort_weight,
        reverse=True
    )

    return results


@frappe.whitelist()
def get_contact_timeline(contact):

    if contact.startswith("FB_"):

        fb_id = contact.replace(
            "FB_",
            ""
        )

        actual_contact = frappe.db.get_value(
            "Contact",
            {
                "custom_facebook_id": fb_id
            },
            "name"
        )

        if actual_contact:
            contact = actual_contact

    return frappe.get_all(
        "CRM Conversation",
        filters={
            "contact": contact
        },
        fields=[
            "name",
            "contact",
            "channel",
            "direction",
            "message",
            "ai_reply",
            "intent",
            "timestamp"
        ],
        order_by="timestamp asc"
    )