import frappe
from openai import OpenAI


def get_openai_client():

    settings = frappe.get_single("AI Settings")

    api_key = settings.get_password("openai_api_key")

    if not api_key:
        frappe.throw("OpenAI API Key not found")

    return OpenAI(api_key=api_key)


def generate_ai_reply(
    message,
    intent=None,
    lead_category=None,
    company=None
):
    """
    Generate AI reply for customer
    """

    client = get_openai_client()

    prompt = f"""
You are a professional AI Sales Assistant.

Customer Message:
{message}

Intent:
{intent}

Lead Category:
{lead_category}

Company:
{company}

Your job:

- Reply professionally
- Reply shortly
- Be human-like
- Encourage customer to continue conversation
- Ask helpful next-step questions
- If customer asks pricing -> ask requirements
- If customer asks service -> explain briefly
- Keep response under 120 words

Return only reply text.
"""

    try:

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI CRM Sales Assistant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.5,
            timeout=20
        )

        reply = response.choices[0].message.content.strip()

        return reply

    except Exception as e:

        frappe.log_error(
            frappe.get_traceback(),
            "AI Reply Engine Error"
        )

        return (
            "Thank you for contacting us. "
            "Our team will get back to you shortly."
        )