import frappe
from datetime import datetime


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
        # DEFAULT VALUES
        # =====================================

        handoff_name = ""
        handoff_status = ""
        handoff_assigned_to = ""

        followup_count = 0
        last_followup_at = ""
        next_followup_due = ""
        sla_status = ""

        days_open = 0

        ai_suggested_reply = ""
        next_best_action = ""

        has_handoff = False

        assigned_to = ""
        todo_count = 0

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

        followup_count = 0
        last_followup_at = ""
        next_followup_due = ""
        sla_status = ""
        days_open = 0
        ai_suggested_reply = ""
        next_best_action = ""
        has_handoff = False

        if ai_lead_name:

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
                fields=[
                    "name",
                    "status",
                    "assigned_to"
                ],
                limit=1,
            )

            if handoffs:

                handoff_name = handoffs[0].get("name") or ""
                handoff_status = handoffs[0].get("status") or ""
                handoff_assigned_to = handoffs[0].get("assigned_to") or ""

                try:

                    hdoc = frappe.get_doc(
                        "AI Handoff",
                        handoff_name
                    )

                    followup_count = getattr(
                        hdoc,
                        "followup_count",
                        0
                    ) or 0

                    last_followup_at = getattr(
                        hdoc,
                        "last_followup_at",
                        ""
                    ) or ""

                    next_followup_due = getattr(
                        hdoc,
                        "next_followup_due",
                        ""
                    ) or ""

                    sla_status = getattr(
                        hdoc,
                        "sla_status",
                        ""
                    ) or ""

                    days_open = getattr(
                        hdoc,
                        "days_open",
                        0
                    ) or 0

                    ai_suggested_reply = getattr(
                        hdoc,
                        "ai_suggested_reply",
                        ""
                    ) or ""

                    next_best_action = getattr(
                        hdoc,
                        "next_best_action",
                        ""
                    ) or ""

                except Exception:
                    frappe.log_error(
                        frappe.get_traceback(),
                        "AI HANDOFF LOAD ERROR"
                    )

                if handoff_assigned_to:
                    assigned_to = handoff_assigned_to

                has_handoff = True

        results.append({
            "contact": display_contact,
            "actual_contact": row.contact,
            "channel": channel_display,
            "messages": row.total_messages,
            "intent": intent,
            "preview": message_preview,
            "lead_category": lead_category,
            "icp_score": icp_score,
            "opportunity": opportunity,
            "handoff_name": handoff_name,
            "handoff_status": handoff_status,
            "handoff_assigned_to": handoff_assigned_to,
            "followup_count": followup_count,
            "last_followup_at": last_followup_at,
            "next_followup_due": next_followup_due,
            "sla_status": sla_status,
            "days_open": days_open,
            "ai_suggested_reply": ai_suggested_reply,
            "next_best_action": next_best_action,
            "ai_reply": ai_suggested_reply,
            "next_action": next_best_action,
            "has_handoff": has_handoff,
            "assigned_to": assigned_to,
            "todo_count": todo_count,
            "last_activity": row.last_activity
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

        # normalize last_activity to numeric timestamp so None is comparable
        la = item.get("last_activity")
        try:
            ts = la.timestamp() if la else 0
        except Exception:
            # if la is not a datetime, fallback to 0
            ts = 0

        return (
            priority,
            item.get("icp_score", 0),
            ts
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

    timeline = []

    # =====================================
    # FACEBOOK CONTACT RESOLUTION
    # =====================================

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

    # =====================================
    # CRM CONVERSATIONS
    # =====================================

    conversations = frappe.get_all(
        "CRM Conversation",
        filters={
            "contact": contact
        },
        fields=[
            "name",
            "channel",
            "direction",
            "message",
            "intent",
            "timestamp"
        ],
        order_by="timestamp asc"
    )

    for row in conversations:

        timeline.append({
            "type": "conversation",
            "timestamp": row.timestamp,
            "title": f"{row.channel} {row.direction}",
            "description": row.message,
            "reference": row.name
        })

    # =====================================
    # AI LEAD
    # =====================================

    ai_lead = frappe.db.get_value(
        "AI Lead",
        {
            "contact": contact
        },
        [
            "name",
            "lead_category",
            "icp_score",
            "custom_erp_lead",
            "custom_erp_opportunity",
            "creation"
        ],
        as_dict=True
    )

    if ai_lead:

        timeline.append({
            "type": "qualification",
            "timestamp": ai_lead.creation,
            "title": "AI Qualified Lead",
            "description":
                f"{ai_lead.lead_category} "
                f"(ICP {ai_lead.icp_score})",
            "reference": ai_lead.name
        })

        if ai_lead.custom_erp_lead:

            timeline.append({
                "type": "erp_lead",
                "timestamp": ai_lead.creation,
                "title": "ERP Lead Created",
                "description":
                    ai_lead.custom_erp_lead,
                "reference":
                    ai_lead.custom_erp_lead
            })

        if ai_lead.custom_erp_opportunity:

            timeline.append({
                "type": "opportunity",
                "timestamp": ai_lead.creation,
                "title": "Opportunity Created",
                "description":
                    ai_lead.custom_erp_opportunity,
                "reference":
                    ai_lead.custom_erp_opportunity
            })

    # =====================================
    # AI HANDOFFS
    # =====================================

    handoffs = frappe.get_all(
        "AI Handoff",
        filters={
            "contact": contact
        },
        fields=[
            "name",
            "assigned_to",
            "status",
            "creation"
        ]
    )

    for row in handoffs:

        timeline.append({
            "type": "handoff",
            "timestamp": row.creation,
            "title": "Lead Assigned",
            "description":
                f"{row.assigned_to} "
                f"({row.status})",
            "reference": row.name
        })

    # =====================================
    # TODOS
    # =====================================

    if ai_lead and ai_lead.custom_erp_opportunity:

        todos = frappe.get_all(
            "ToDo",
            filters={
                "reference_type":
                    "Opportunity",
                "reference_name":
                    ai_lead.custom_erp_opportunity
            },
            fields=[
                "name",
                "status",
                "allocated_to",
                "creation"
            ]
        )

        for row in todos:

            timeline.append({
                "type": "todo",
                "timestamp": row.creation,
                "title": "Follow-up Task",
                "description":
                    f"{row.allocated_to} "
                    f"({row.status})",
                "reference": row.name
            })

    # =====================================
    # SORT TIMELINE
    # =====================================

    timeline.sort(
        key=lambda x: x["timestamp"]
        if x["timestamp"] else "",
        reverse=False
    )

    return timeline


@frappe.whitelist()
def get_workspace_data(handoff_name):

    if not handoff_name:
        return {"error": "missing_handoff_name"}

    try:
        handoff = frappe.get_doc("AI Handoff", handoff_name)

        conversations = frappe.get_all(
            "CRM Conversation",
            filters={"contact": handoff.contact},
            fields=["channel", "direction", "message", "timestamp"],
            order_by="timestamp desc",
            limit=50,
        )

        todos = []

        if handoff.opportunity:

            todos = frappe.get_all(
                "ToDo",
                filters={
                    "reference_type": "Opportunity",
                    "reference_name": handoff.opportunity
                },
                fields=[
                    "name",
                    "description",
                    "status"
                ],
            )

        return {
            "handoff": handoff.as_dict(),
            "timeline": conversations,
            "todos": todos,
            "copilot": {
                "reply": handoff.get("ai_suggested_reply"),
                "action": handoff.get("next_best_action"),
            },
        }

    except Exception:
        frappe.log_error(frappe.get_traceback(), "get_workspace_data_error")
        return {"error": "exception"}


@frappe.whitelist()
def assign_handoff(
    handoff,
    assigned_to=None
):

    if not handoff:
        return {
            "success": False,
            "error": "missing_handoff"
        }

    doc = frappe.get_doc(
        "AI Handoff",
        handoff
    )

    if not assigned_to:
        assigned_to = frappe.session.user

    doc.assigned_to = assigned_to

    if doc.status == "Open":
        doc.status = "Assigned"
    doc.flags.ignore_version = True
    doc.save(
        ignore_permissions=True
    )

    frappe.db.commit()

    return {
        "success": True,
        "handoff": doc.name,
        "assigned_to": assigned_to
    }

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
    doc.flags.ignore_version = True
    doc.save(ignore_permissions=True)
    frappe.db.commit()

    return {"success": True, "handoff": handoff}


@frappe.whitelist()
def close_handoff(handoff):
    if not handoff:
        return {"success": False, "error": "missing_handoff"}

    doc = frappe.get_doc("AI Handoff", handoff)
    doc.status = "Closed"
    doc.flags.ignore_version = True
    doc.save(ignore_permissions=True)
    frappe.db.commit()

    return {"success": True, "handoff": handoff}
@frappe.whitelist()
def close_won(handoff):

    if not handoff:
        return {
            "success": False,
            "error": "missing_handoff"
        }

    doc = frappe.get_doc(
        "AI Handoff",
        handoff
    )

    if doc.opportunity:

        opp = frappe.get_doc(
            "Opportunity",
            doc.opportunity
        )

        opp.reload()

        opp.status = "Converted"
        doc.flags.ignore_version = True
        opp.save(
            ignore_permissions=True
        )

        todos = frappe.get_all(
            "ToDo",
            filters={
                "reference_type": "Opportunity",
                "reference_name": opp.name,
                "status": ["!=", "Closed"]
            },
            pluck="name"
        )

        for todo_name in todos:

            todo = frappe.get_doc(
                "ToDo",
                todo_name
            )

            todo.status = "Closed"
            doc.flags.ignore_version = True

            todo.save(
                ignore_permissions=True
            )

    doc.reload()

    doc.status = "Closed Won"
    doc.flags.ignore_version = True
    doc.save(
        ignore_permissions=True
    )

    frappe.db.commit()

    return {
        "success": True,
        "handoff": handoff,
        "result": "won"
    }
@frappe.whitelist()
def close_lost(handoff):

    if not handoff:
        return {
            "success": False,
            "error": "missing_handoff"
        }

    doc = frappe.get_doc(
        "AI Handoff",
        handoff
    )

    if doc.opportunity:

        opp = frappe.get_doc(
            "Opportunity",
            doc.opportunity
        )

        opp.reload()

        opp.status = "Lost"
        doc.flags.ignore_version = True
        opp.save(
            ignore_permissions=True
        )

    doc.reload()

    doc.status = "Closed Lost"
    
    doc.flags.ignore_version = True
    doc.save(
        ignore_permissions=True
    )

    frappe.db.commit()

    return {
        "success": True,
        "handoff": handoff,
        "result": "lost"
    }