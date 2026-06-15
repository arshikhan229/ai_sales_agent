import frappe
from datetime import datetime


def get_unified_conversations(limit=500):
    """Aggregate latest CRM Conversation per contact and enrich with AI Lead/ERP Lead info.

    Returns list of dicts with keys:
    contact, channel, lead, last_message, last_activity, priority, icp_score, lead_score
    """
    try:
        contacts = frappe.db.sql(
            """
            SELECT
                contact,
                COUNT(*) as total_messages,
                MAX(timestamp) as last_activity
            FROM `tabCRM Conversation`
            GROUP BY contact
            ORDER BY last_activity DESC
            LIMIT %s
        """,
            (limit,),
            as_dict=True,
        )

        results = []

        for row in contacts:
            latest = frappe.db.sql(
                """
                SELECT
                    message,
                    channel,
                    timestamp
                FROM `tabCRM Conversation`
                WHERE contact=%s
                ORDER BY timestamp DESC
                LIMIT 1
                """,
                (row.contact,),
                as_dict=True,
            )

            latest = latest[0] if latest else {}

            last_message = latest.get("message", "")
            channel = latest.get("channel", "")
            last_activity = row.get("last_activity")

            # AI Lead enrichment
            ai_lead_name = frappe.db.get_value("AI Lead", {"contact": row.contact}, "name")
            priority = ""
            icp_score = 0
            lead_score = 0
            erp_lead = ""

            if ai_lead_name:
                try:
                    ai_lead = frappe.get_doc("AI Lead", ai_lead_name)
                    priority = (ai_lead.lead_category or "")
                    icp_score = float(getattr(ai_lead, "icp_score", 0) or 0)
                    lead_score = float(getattr(ai_lead, "lead_score", 0) or 0)

                    # Map to ERP Next Lead where possible
                    if getattr(ai_lead, "email", None):
                        erp_lead = frappe.db.get_value("Lead", {"email_id": ai_lead.email}, "name") or ""

                    if not erp_lead and getattr(ai_lead, "lead_name", None):
                        erp_lead = frappe.db.get_value("Lead", {"lead_name": ai_lead.lead_name}, "name") or ""

                except Exception:
                    frappe.log_error(frappe.get_traceback(), "inbox_ai_lead_lookup_error")

            results.append({
                "contact": row.contact,
                "channel": channel,
                "lead": erp_lead or "",
                "last_message": last_message,
                "last_activity": last_activity,
                "priority": priority,  # Hot|Warm|Cold
                "icp_score": icp_score,
                "lead_score": lead_score,
                "total_messages": int(row.total_messages or 0),
            })

        # Sorting: 1) Lead Category (Hot>Warm>Cold) 2) ICP score desc 3) Lead score desc 4) Last activity desc
        def sort_key(item):
            cat = (item.get("priority") or "").lower()
            if "hot" in cat:
                weight = 3
            elif "warm" in cat:
                weight = 2
            else:
                weight = 1

            icp = item.get("icp_score") or 0
            ls = item.get("lead_score") or 0
            la = item.get("last_activity")
            try:
                ts = la.timestamp() if la else 0
            except Exception:
                ts = 0
            # reverse sort by returning tuple used with reverse=True
            return (weight, icp, ls, ts)

        results.sort(key=sort_key, reverse=True)

        return results

    except Exception:
        frappe.log_error(frappe.get_traceback(), "get_unified_conversations_error")
        return []
