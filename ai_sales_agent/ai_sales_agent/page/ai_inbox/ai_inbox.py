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

    # Counters
    total_handoffs = frappe.db.count("AI Handoff")
    open_handoffs = frappe.db.sql(
        "SELECT COUNT(*) FROM `tabAI Handoff` WHERE status != %s",
        ("Closed",),
    )

    open_handoffs = (open_handoffs[0][0] if open_handoffs else 0) or 0

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

        assigned_to = ""

        todo_count = 0

        if opportunity:

            todo_count = frappe.db.count(
                "ToDo",
                {
                    "reference_type":
                        "Opportunity",

                    "reference_name":
                        opportunity
                }
            )

            todo = frappe.get_all(
                "ToDo",
                filters={
                    "reference_type":
                        "Opportunity",

                    "reference_name":
                        opportunity
                },
                fields=["allocated_to"],
                limit=1
            )

            if todo:
                assigned_to = (
                    todo[0].allocated_to
                )

        # =====================================
        # AI HANDOFF LOOKUP
        # =====================================

        handoff_name = ""
        handoff_status = ""
        handoff_assigned_to = ""

        if ai_lead_name:
            # Audit: log lookup key (AI Lead.name)
            try:
                frappe.logger().info(
                    f"INBOX HANDOFF LOOKUP => lead={ai_lead_name}"
                )
            except Exception:
                pass

            handoffs = frappe.get_all(
                "AI Handoff",
                filters=[
                    ["AI Handoff", "lead", "=", ai_lead_name],
                    ["AI Handoff", "status", "!=", "Closed"],
                ],
                fields=["name", "status", "assigned_to"],
                limit=1,
            )

            if handoffs:
                handoff_name = handoffs[0].get("name") or ""
                handoff_status = handoffs[0].get("status") or ""
                handoff_assigned_to = handoffs[0].get("assigned_to") or ""

                # log found handoff
                try:
                    frappe.logger().info(
                        f"FOUND HANDOFF => {handoff_name}"
                    )
                except Exception:
                    pass

                # prefer handoff assigned_to over todo assigned
                if handoff_assigned_to:
                    assigned_to = handoff_assigned_to
                has_handoff = True
            else:
                has_handoff = False

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

            "handoff_name":
                handoff_name,

            "handoff_status":
                handoff_status,

            "handoff_assigned_to":
                handoff_assigned_to,

            "has_handoff":
                bool(handoff_name),

            "assigned_to":
                assigned_to,

            "todo_count":
                todo_count,

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

    return {
        "rows": results,
        "total_handoffs": total_handoffs,
        "open_handoffs": open_handoffs,
    }


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


@frappe.whitelist()
def get_handoffs(filter_type=None):
    """Return handoffs for the inbox with simple filters.

    filter_type: Open | Assigned To Me | All
    """
    filters = {}

    if filter_type == "Open":
        filters["status"] = "Open"

    elif filter_type == "Assigned To Me":
        filters["assigned_to"] = frappe.session.user

    # else: All (no additional filters)

    handoffs = frappe.get_all(
        "AI Handoff",
        filters=filters,
        fields=[
            "name",
            "lead",
            "contact",
            "channel",
            "assigned_to",
            "status",
            "priority",
            "opportunity",
            "creation",
        ],
        order_by="creation desc",
        limit=500,
    )

    return handoffs


@frappe.whitelist()
def assign_handoff_to_me(handoff):
    if not handoff:
        return {
            "success": False,
            "error": "missing_handoff",
        }

    doc = frappe.get_doc("AI Handoff", handoff)
    doc.assigned_to = frappe.session.user
    doc.status = "Assigned"
    doc.save(ignore_permissions=True)
    frappe.db.commit()

    return {"success": True, "handoff": handoff}


@frappe.whitelist()
def close_handoff(handoff):
    if not handoff:
        return {"success": False, "error": "missing_handoff"}

    doc = frappe.get_doc("AI Handoff", handoff)
    doc.status = "Closed"
    doc.save(ignore_permissions=True)
    frappe.db.commit()

    return {"success": True, "handoff": handoff}