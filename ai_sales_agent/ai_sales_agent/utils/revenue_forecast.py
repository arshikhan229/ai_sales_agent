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
def get_revenue_forecast():

    pipeline_value = 0
    forecast_value = 0
    won_value = 0

    opportunities = frappe.get_all(
        "Opportunity",
        fields=[
            "name",
            "opportunity_amount",
            "custom_pipeline_stage"
        ]
    )

    for opp in opportunities:

        amount = (
            opp.opportunity_amount
            or 0
        )

        stage = (
            opp.custom_pipeline_stage
            or "Qualified"
        )

        probability = STAGE_PROBABILITY.get(
            stage,
            20
        )

        pipeline_value += amount

        forecast_value += (
            amount *
            probability / 100
        )

        if stage == "Closed Won":
            won_value += amount

    return {
        "pipeline_value": pipeline_value,
        "forecast_value": forecast_value,
        "won_value": won_value
    }
