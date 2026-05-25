def calculate_icp_score(
    message="",
    email="",
    company=""
):
    score = 0

    message = (message or "").lower()
    email = (email or "").lower()
    company = (company or "").lower()

    hot_keywords = [
        "pricing",
        "price",
        "cost",
        "demo",
        "buy",
        "purchase",
        "quotation",
        "quote",
        "urgent",
        "implementation",
        "erpnext",
        "crm",
        "software",
        "payment",
        "invoice",
        "order",
        "amount",
        "bill",
        "$",
        "usd",
        "deal",
        "system",
        "project"
    ]

    for word in hot_keywords:
        if word in message:
            score += 15

    free_domains = [
        "gmail.com",
        "yahoo.com",
        "hotmail.com",
        "outlook.com"
    ]

    if email and "@" in email:

        domain = email.split("@")[-1]

        if domain not in free_domains:
            score += 20

    if company:
        score += 20

    score = min(score, 100)

    return score


def get_lead_category(score):

    if score >= 40:
        return "Hot"

    elif score >= 20:
        return "Warm"

    return "Cold"