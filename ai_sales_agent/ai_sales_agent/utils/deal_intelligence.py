import frappe


def analyze_opportunity(opportunity):

    doc = frappe.get_doc(
        "Opportunity",
        opportunity
    )

    score = 50

    stage = (
        doc.custom_pipeline_stage
        or "Qualified"
    )

    if stage == "Discovery":
        score += 10

    elif stage == "Proposal":
        score += 20

    elif stage == "Negotiation":
        score += 30

    elif stage == "Closed Won":
        score = 100

    probability_map = {
        "Qualified": 20,
        "Discovery": 40,
        "Proposal": 60,
        "Negotiation": 80,
        "Closed Won": 100,
        "Closed Lost": 0
    }

    probability = probability_map.get(
        stage,
        20
    )

    if probability >= 80:
        risk = "Low"

    elif probability >= 40:
        risk = "Medium"

    else:
        risk = "High"

    next_action = {
        "Qualified":
            "Contact lead",

        "Discovery":
            "Schedule discovery call",

        "Proposal":
            "Send proposal",

        "Negotiation":
            "Follow up on pricing",

        "Closed Won":
            "Start onboarding",

        "Closed Lost":
            "Archive opportunity"
    }.get(stage)

    summary = (
        f"Opportunity currently in "
        f"{stage} stage."
    )

    reply = (
        "Thank you for your interest. "
        "We would be happy to discuss "
        "the next steps."
    )

    doc.custom_ai_deal_score = score
    doc.custom_win_probability = probability
    doc.custom_risk_level = risk
    doc.custom_next_best_action = next_action
    doc.custom_ai_summary = summary
    doc.custom_suggested_reply = reply
    doc.custom_last_ai_analysis = frappe.utils.now_datetime()

    doc.save(
        ignore_permissions=True
    )

    return {
        "score": score,
        "probability": probability,
        "risk": risk
    }
