import frappe
from openai import OpenAI


def get_openai_client():
    """
    Get OpenAI client from AI Settings
    """

    settings = frappe.get_single(
        "AI Settings"
    )

    api_key = settings.get_password(
        "openai_api_key"
    )

    if not api_key:

        frappe.throw(
            "OpenAI API Key not found in AI Settings"
        )

    return OpenAI(
        api_key=api_key
    )


def generate_ai_reply(
    message,
    intent=None,
    lead_category=None,
    company=None,
    channel=None,
    context=None
):
    """
    Generate intelligent CRM reply
    """

    client = get_openai_client()

    context = context or "No previous conversation history."

    prompt = f"""
You are a professional ERPNext CRM Sales Consultant.

Business Services:

- ERPNext Implementation
- ERPNext Support
- CRM Automation
- AI Lead Qualification
- Business Process Automation
- Custom ERP Development
- Workflow Automation
- Inventory Management
- Procurement Automation

Customer History:
{context}

Current Customer Message:
{message}

Intent:
{intent}

Lead Category:
{lead_category}

Company:
{company}

Channel:
{channel}

Instructions:

1. Reply professionally.

2. Reply naturally like a human.

3. Use previous conversation history if available.

4. Never repeat questions already answered by customer.

5. Keep response under 120 words.

6. Encourage customer to continue discussion.

7. Ask one useful qualification question.

8. If Pricing Inquiry:
   ask company size,
   number of users,
   required modules.

9. If Demo Request:
   ask preferred date and time.

10. If Product Inquiry:
    briefly explain solution
    and ask requirements.

11. If Support Request:
    ask issue details.

12. If customer already provided
    company size or requirements,
    do not ask again.

13. End with one clear next step.

Return only reply text.
"""

    try:

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content":
                    """
You are an expert ERPNext CRM sales assistant.

Rules:

- Be concise.
- Be professional.
- Be helpful.
- Use conversation history.
- Never use markdown.
- Return plain text only.
"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.5,
            timeout=20
        )

        reply = (
            response
            .choices[0]
            .message
            .content
            .strip()
        )

        return reply

    except Exception:

        frappe.log_error(
            frappe.get_traceback(),
            "AI Reply Engine Error"
        )

        return (
            "Thank you for contacting us. "
            "We have received your inquiry and "
            "our team will respond shortly. "
            "Could you please share more details "
            "about your requirements?"
        )