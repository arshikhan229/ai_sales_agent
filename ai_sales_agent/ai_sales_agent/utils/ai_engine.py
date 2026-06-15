import frappe
import json
from openai import OpenAI

from ai_sales_agent.ai_sales_agent.utils.scoring import (
    calculate_icp_score,
    get_lead_category,
    has_hot_buying_signal,
)

from ai_sales_agent.ai_sales_agent.utils.context_builder import (
    build_lead_context
)

from ai_sales_agent.ai_sales_agent.utils.intent_engine import (
    normalize_intent
)


def get_openai_client():

    settings = frappe.get_single("AI Settings")

    api_key = settings.get_password(
        "openai_api_key"
    )

    if not api_key:
        frappe.throw(
            "OpenAI API Key not set in AI Settings"
        )

    return OpenAI(api_key=api_key)


def analyze_lead(
    message,
    email=None,
    company=None
):

    client = get_openai_client()

    context = build_lead_context(email)

    prompt = f"""
You are an ERPNext Sales Qualification AI.

Customer History:
{context}

Customer Message:
{message}

Email:
{email}

Company:
{company}

Intent Types:

- Pricing Inquiry
- Product Inquiry
- Demo Request
- Support Request
- Billing Inquiry
- Complaint
- Partnership Inquiry
- General Inquiry

Rules:

1. If customer asks about cost, pricing, quotation, budget, proposal or implementation cost -> Pricing Inquiry

2. If customer asks for ERPNext demo -> Demo Request

3. If customer asks product features -> Product Inquiry

4. If customer asks technical help -> Support Request

Return STRICT JSON only.

Example:

{{
  "intent_type":"Pricing Inquiry",
  "intent_confidence":0.95,
  "reason":"Customer is requesting ERPNext pricing information."
}}
"""

    try:

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content":
                    "Return valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2
        )

        content = (
            response
            .choices[0]
            .message
            .content
            .strip()
        )

        content = (
            content
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        data = json.loads(content)
        normalized_intent = normalize_intent(
            data.get(
                "intent_type",
                "General Inquiry"
            )
        )

        score = calculate_icp_score(
            message=message,
            email=email,
            company=company
        )

        if has_hot_buying_signal(
            message=message,
            intent_type=normalized_intent,
        ) or normalized_intent == "Partnership Inquiry":
            category = "Hot"

        elif normalized_intent == "Product Inquiry":
            category = "Warm"

        else:
            category = get_lead_category(score)

        return {
            "intent_type": normalized_intent,
            "intent_confidence":
                float(
                    data.get(
                        "intent_confidence",
                        0
                    )
                ),
            "icp_score": score,
            "lead_category": category,
            "reason":
                data.get(
                    "reason",
                    ""
                )
        }

    except Exception:

        frappe.log_error(
            frappe.get_traceback(),
            "AI Engine Error"
        )

        score = calculate_icp_score(
            message=message,
            email=email,
            company=company
        )
        category = (
            "Hot"
            if has_hot_buying_signal(message=message)
            else get_lead_category(score)
        )

        return {
            "intent_type": "General Inquiry",
            "intent_confidence": 0,
            "icp_score": score,
            "lead_category": category,
            "reason": "AI analysis failed"
        }
