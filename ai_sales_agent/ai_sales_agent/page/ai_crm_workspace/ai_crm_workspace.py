import frappe


@frappe.whitelist()
def get_dashboard_data():

    hot_leads = frappe.db.count(
        "AI Lead",
        {"lead_category": "Hot"}
    )

    open_handoffs = frappe.db.count(
        "AI Handoff",
        {"status": "Open"}
    )

    pipeline_value = frappe.db.sql("""
        select ifnull(sum(opportunity_amount),0)
        from `tabOpportunity`
        where status='Open'
    """)[0][0]

    return {
        "hot_leads": hot_leads,
        "open_handoffs": open_handoffs,
        "pipeline_value": pipeline_value
    }


@frappe.whitelist()
def get_customers():

    return frappe.get_all(
        "AI Lead",
        fields=[
            "name",
            "lead_name",
            "source",
            "lead_category",
            "custom_erp_opportunity"
        ],
        order_by="modified desc",
        limit=50
    )


@frappe.whitelist()
def get_handoffs():

    return frappe.get_all(
        "AI Handoff",
        fields=[
            "name",
            "assigned_to",
            "status",
            "opportunity"
        ],
        order_by="creation desc",
        limit=50
    )


@frappe.whitelist()
def get_forecast():

    from ai_sales_agent.ai_sales_agent.utils.revenue_forecast import (
        get_revenue_forecast
    )

    return get_revenue_forecast()


@frappe.whitelist()
def get_analytics():

    return {
        "whatsapp": frappe.db.count(
            "AI Lead",
            {"source": "WhatsApp"}
        ),

        "facebook": frappe.db.count(
            "AI Lead",
            {"source": "Facebook"}
        ),

        "email": frappe.db.count(
            "AI Lead",
            {"source": "Email"}
        ),

        "hot": frappe.db.count(
            "AI Lead",
            {"lead_category": "Hot"}
        ),

        "warm": frappe.db.count(
            "AI Lead",
            {"lead_category": "Warm"}
        ),

        "cold": frappe.db.count(
            "AI Lead",
            {"lead_category": "Cold"}
        )
    }


@frappe.whitelist()
def get_pipeline_summary():

    return frappe.db.sql("""
        select
            ifnull(custom_pipeline_stage,'Qualified') as stage,
            count(*) as total,
            ifnull(sum(opportunity_amount),0) as amount
        from `tabOpportunity`
        group by custom_pipeline_stage
        order by total desc
    """, as_dict=True)

@frappe.whitelist()
def get_recent_hot_leads():

    return frappe.get_all(
        "AI Lead",
        filters={
            "lead_category": "Hot"
        },
        fields=[
            "name",
            "lead_name",
            "source",
            "intent_type",
            "icp_score"
        ],
        order_by="modified desc",
        limit=10
    )


@frappe.whitelist()
def get_recent_opportunities():

    return frappe.get_all(
        "Opportunity",
        fields=[
            "name",
            "custom_pipeline_stage",
            "opportunity_amount",
            "custom_win_probability"
        ],
        order_by="modified desc",
        limit=10
    )


@frappe.whitelist()
def get_recent_activities():

    rows = []

    conversations = frappe.get_all(
        "CRM Conversation",
        fields=[
            "message",
            "channel",
            "timestamp"
        ],
        order_by="timestamp desc",
        limit=10
    )

    for c in conversations:

        rows.append({
            "type": "Conversation",
            "title": c.message,
            "channel": c.channel,
            "timestamp": c.timestamp
        })

    handoffs = frappe.get_all(
        "AI Handoff",
        fields=[
            "assigned_to",
            "status",
            "creation"
        ],
        order_by="creation desc",
        limit=10
    )

    for h in handoffs:

        rows.append({
            "type": "Handoff",
            "title": f"Assigned to {h.assigned_to}",
            "status": h.status,
            "timestamp": h.creation
        })

    rows.sort(
        key=lambda x: x["timestamp"],
        reverse=True
    )

    return rows[:15]

@frappe.whitelist()
def get_pipeline_board():

    return frappe.get_all(
        "Opportunity",
        fields=[
            "name",
            "custom_pipeline_stage",
            "opportunity_amount",
            "custom_win_probability"
        ],
        order_by="modified desc",
        limit=100
    )

@frappe.whitelist()
def get_dashboard_v2():

    forecast = get_forecast()

    return {
        "hot_leads": frappe.db.count(
            "AI Lead",
            {"lead_category": "Hot"}
        ),

        "open_handoffs": frappe.db.count(
            "AI Handoff",
            {"status": ["!=", "Closed"]}
        ),

        "pipeline_value": forecast.get(
            "pipeline_value",
            0
        ),

        "forecast_value": forecast.get(
            "forecast_value",
            0
        ),

        "recent_leads": get_recent_hot_leads(),

        "recent_opportunities":
            get_recent_opportunities(),

        "recent_activities":
            get_recent_activities()
    }

@frappe.whitelist()
def get_ai_alerts():

    alerts = []

    low_probability = frappe.get_all(
        "Opportunity",
        filters={
            "custom_win_probability": ["<", 30]
        },
        fields=[
            "name",
            "custom_win_probability"
        ],
        limit=10
    )

    for row in low_probability:

        alerts.append({
            "type": "Opportunity",
            "message":
            f"{row.name} has win probability {row.custom_win_probability}%"
        })

    overdue_handoffs = frappe.get_all(
        "AI Handoff",
        filters={
            "sla_status": "Overdue"
        },
        fields=[
            "name",
            "assigned_to"
        ],
        limit=10
    )

    for row in overdue_handoffs:

        alerts.append({
            "type": "Handoff",
            "message":
            f"{row.name} is overdue"
        })

    return alerts

@frappe.whitelist()
def get_command_center():

    hot_leads = frappe.db.count(
        "AI Lead",
        {"lead_category": "Hot"}
    )

    risk_deals = frappe.db.count(
        "Opportunity",
        {"custom_risk_level": "High"}
    )

    followups = frappe.db.count(
        "ToDo",
        {"status": "Open"}
    )

    handoffs = frappe.db.count(
        "AI Handoff",
        {"status": "Open"}
    )

    top_opportunities = frappe.get_all(
        "Opportunity",
        fields=[
            "name",
            "opportunity_amount",
            "custom_win_probability"
        ],
        order_by="opportunity_amount desc",
        limit=5
    )

    return {
        "hot_leads": hot_leads,
        "risk_deals": risk_deals,
        "followups": followups,
        "handoffs": handoffs,
        "top_opportunities": top_opportunities
    }

@frappe.whitelist()
def get_customer_health_scores():

    rows = frappe.get_all(
        "AI Lead",
        fields=[
            "name",
            "lead_name",
            "lead_category",
            "custom_erp_opportunity"
        ],
        limit=100
    )

    result = []

    for row in rows:

        score = 50

        if row.lead_category == "Hot":
            score += 20

        elif row.lead_category == "Warm":
            score += 10

        if row.custom_erp_opportunity:
            score += 20

        if score >= 70:
            status = "Healthy"

        elif score >= 40:
            status = "Watch"

        else:
            status = "At Risk"

        result.append({
            "name": row.name,
            "lead_name": row.lead_name,
            "score": score,
            "status": status
        })

    return result

@frappe.whitelist()
def get_pipeline_health():

    likely_close = frappe.db.count(
        "Opportunity",
        {
            "custom_win_probability": [">=", 70]
        }
    )

    high_risk = frappe.db.count(
        "Opportunity",
        {
            "custom_risk_level": "High"
        }
    )

    big_deals = frappe.db.sql("""
        select count(*)
        from `tabOpportunity`
        where opportunity_amount >= 100000
    """)[0][0]

    stuck = frappe.db.sql("""
        select count(*)
        from `tabOpportunity`
        where modified < DATE_SUB(NOW(), INTERVAL 14 DAY)
    """)[0][0]

    return {
        "likely_close": likely_close,
        "high_risk": high_risk,
        "big_deals": big_deals,
        "stuck": stuck
    }


@frappe.whitelist()
def get_pipeline_health_details():

    likely_close = frappe.get_all(
        "Opportunity",
        filters={
            "custom_win_probability": [">=", 70]
        },
        fields=[
            "name",
            "opportunity_amount",
            "custom_win_probability"
        ],
        limit=20
    )

    risk_deals = frappe.get_all(
        "Opportunity",
        filters={
            "custom_risk_level": "High"
        },
        fields=[
            "name",
            "opportunity_amount",
            "custom_risk_level"
        ],
        limit=20
    )

    return {
        "likely_close": likely_close,
        "risk_deals": risk_deals
    }


@frappe.whitelist()
def get_deal_risk_engine():

    opportunities = frappe.get_all(
        "Opportunity",
        fields=[
            "name",
            "custom_win_probability",
            "custom_ai_deal_score",
            "custom_pipeline_stage",
            "modified",
            "opportunity_amount"
        ],
        limit=100
    )

    result = []

    from frappe.utils import now_datetime

    for opp in opportunities:

        risk_score = 0

        if (opp.custom_win_probability or 0) < 30:
            risk_score += 30

        if (opp.custom_ai_deal_score or 0) < 40:
            risk_score += 20

        if opp.custom_pipeline_stage == "Qualified":
            risk_score += 15

        if opp.modified:

            days = (
                now_datetime() -
                opp.modified
            ).days

            if days > 14:
                risk_score += 25

        if risk_score >= 70:
            status = "Critical"

        elif risk_score >= 40:
            status = "At Risk"

        else:
            status = "Healthy"

        result.append({

            "name": opp.name,

            "amount":
                opp.opportunity_amount,

            "risk_score":
                risk_score,

            "status":
                status
        })

    return result

@frappe.whitelist()
def get_ai_recommendations():

    recommendations = []

    hot_leads = frappe.get_all(
        "AI Lead",
        filters={
            "lead_category": "Hot"
        },
        fields=[
            "name",
            "lead_name",
            "custom_erp_opportunity"
        ],
        limit=20
    )

    for lead in hot_leads:

        if not lead.custom_erp_opportunity:

            recommendations.append({

                "priority": "High",

                "type": "Lead",

                "message":
                f"Create opportunity for {lead.lead_name}"

            })

    risk_deals = frappe.get_all(
        "Opportunity",
        filters={
            "custom_risk_level": "High"
        },
        fields=[
            "name"
        ],
        limit=20
    )

    for deal in risk_deals:

        recommendations.append({

            "priority": "High",

            "type": "Deal",

            "message":
            f"Review risky deal {deal.name}"

        })

    open_handoffs = frappe.get_all(
        "AI Handoff",
        filters={
            "status": "Open"
        },
        fields=[
            "name"
        ],
        limit=20
    )

    for handoff in open_handoffs:

        recommendations.append({

            "priority": "Medium",

            "type": "Handoff",

            "message":
            f"Resolve handoff {handoff.name}"

        })

    return recommendations[:25]