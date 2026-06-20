import frappe


STAGE_PROBABILITY = {
    "Qualified": 20,
    "Discovery": 40,
    "Proposal": 60,
    "Negotiation": 80,
    "Closed Won": 100,
    "Closed Lost": 0
}


@frappe.whitelist()
def get_pipeline_data():

    stages = {
        "Qualified": [],
        "Discovery": [],
        "Proposal": [],
        "Negotiation": [],
        "Closed Won": [],
        "Closed Lost": []
    }

    stage_totals = {
        "Qualified": 0,
        "Discovery": 0,
        "Proposal": 0,
        "Negotiation": 0,
        "Closed Won": 0,
        "Closed Lost": 0
    }

    total_pipeline_value = 0
    total_forecast_value = 0

    opportunities = frappe.get_all(
        "Opportunity",
        fields=[
            "name",
            "party_name",
            "opportunity_amount",
            "custom_pipeline_stage",
            "modified"
        ],
        order_by="modified desc"
    )

    for row in opportunities:

        stage = (
            row.custom_pipeline_stage
            or "Qualified"
        )

        if stage not in stages:
            stage = "Qualified"

        amount = float(
            row.opportunity_amount or 0
        )

        probability = STAGE_PROBABILITY.get(
            stage,
            0
        )

        forecast = (
            amount * probability / 100
        )

        row.probability = probability
        row.forecast_amount = forecast

        stages[stage].append(row)

        stage_totals[stage] += amount

        total_pipeline_value += amount
        total_forecast_value += forecast

    return {
        "stages": stages,
        "stage_totals": stage_totals,
        "total_pipeline_value": total_pipeline_value,
        "total_forecast_value": total_forecast_value
    }


@frappe.whitelist()
def update_pipeline_stage(
    opportunity,
    stage
):

    doc = frappe.get_doc(
        "Opportunity",
        opportunity
    )

    doc.custom_pipeline_stage = stage

    if stage == "Closed Won":
        doc.status = "Closed"

    elif stage == "Closed Lost":
        doc.status = "Closed"

    else:
        doc.status = "Open"

    doc.save(
        ignore_permissions=True
    )

    frappe.db.commit()

    return {
        "success": True
    }