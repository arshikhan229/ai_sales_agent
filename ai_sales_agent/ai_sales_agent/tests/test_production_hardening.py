import base64
import hashlib
import hmac
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from ai_sales_agent.ai_sales_agent.utils.lead_filter import (
    should_process_email,
)
from ai_sales_agent.ai_sales_agent.utils.webhook_security import (
    validate_facebook_request,
    validate_twilio_request,
)


class FakeRequest:
    def __init__(self, headers=None, url="", form=None, body=b""):
        self.headers = headers or {}
        self.url = url
        self.form = form or {}
        self._body = body

    def get_data(self):
        return self._body


class TestWebhookSecurity(unittest.TestCase):
    def test_valid_twilio_signature(self):
        token = "twilio-secret"
        url = "https://example.com/api/method/ai_sales_agent.api.whatsapp"
        form = {
            "Body": "Need ERPNext pricing",
            "From": "whatsapp:+15551234567",
        }
        payload = url + "".join(
            f"{key}{form[key]}"
            for key in sorted(form.keys())
        )
        signature = base64.b64encode(
            hmac.new(
                token.encode("utf-8"),
                payload.encode("utf-8"),
                hashlib.sha1,
            ).digest()
        ).decode("ascii")

        request = FakeRequest(
            headers={"X-Twilio-Signature": signature},
            url=url,
            form=form,
        )

        with patch(
            "ai_sales_agent.ai_sales_agent.utils.webhook_security._get_ai_settings_password",
            return_value=token,
        ):
            self.assertTrue(validate_twilio_request(request))

    def test_invalid_twilio_signature(self):
        request = FakeRequest(
            headers={"X-Twilio-Signature": "bad"},
            url="https://example.com/webhook",
            form={"Body": "Hello"},
        )

        with patch(
            "ai_sales_agent.ai_sales_agent.utils.webhook_security._get_ai_settings_password",
            return_value="twilio-secret",
        ):
            self.assertFalse(validate_twilio_request(request))

    def test_valid_facebook_signature(self):
        secret = "facebook-secret"
        body = b'{"object":"page"}'
        signature = "sha256=" + hmac.new(
            secret.encode("utf-8"),
            body,
            hashlib.sha256,
        ).hexdigest()
        request = FakeRequest(
            headers={"X-Hub-Signature-256": signature},
            body=body,
        )

        with patch(
            "ai_sales_agent.ai_sales_agent.utils.webhook_security._get_ai_settings_password",
            return_value=secret,
        ):
            self.assertTrue(validate_facebook_request(request))

    def test_invalid_facebook_signature(self):
        request = FakeRequest(
            headers={"X-Hub-Signature-256": "sha256=bad"},
            body=b"{}",
        )

        with patch(
            "ai_sales_agent.ai_sales_agent.utils.webhook_security._get_ai_settings_password",
            return_value="facebook-secret",
        ):
            self.assertFalse(validate_facebook_request(request))


class TestEmailFiltering(unittest.TestCase):
    def test_sales_email_is_accepted(self):
        result = should_process_email(
            "buyer@example.com",
            "ERPNext pricing",
            "Need implementation quote",
        )
        self.assertTrue(result["process"])

    def test_marketing_email_is_rejected(self):
        cases = [
            (
                "news@example.com",
                "Weekly Newsletter",
                "ERP updates",
                None,
                "newsletter",
            ),
            (
                "hello@example.com",
                "Daily Digest",
                "ERP updates",
                None,
                "newsletter",
            ),
            (
                "noreply@example.com",
                "ERPNext pricing",
                "Need pricing",
                None,
                "system_sender",
            ),
            (
                "buyer@example.com",
                "ERPNext pricing",
                "Need pricing",
                {"List-Unsubscribe": "<mailto:x>"},
                "list_unsubscribe",
            ),
        ]

        for sender, subject, content, headers, reason in cases:
            with self.subTest(sender=sender, subject=subject):
                result = should_process_email(
                    sender,
                    subject,
                    content,
                    headers=headers,
                )
                self.assertFalse(result["process"])
                self.assertEqual(result["reason"], reason)


class TestTodoLifecycleLookup(unittest.TestCase):
    def test_handoff_and_opportunity_todos_are_returned(self):
        from ai_sales_agent.ai_sales_agent.utils.claim_engine import (
            _get_related_todos,
        )

        handoff = SimpleNamespace(
            name="HANDOFF-1",
            opportunity="OPP-1",
        )

        def fake_get_all(doctype, filters=None, fields=None):
            if filters == [
                ["ToDo", "reference_type", "=", "AI Handoff"],
                ["ToDo", "reference_name", "=", "HANDOFF-1"],
            ]:
                return [SimpleNamespace(name="TODO-HANDOFF")]

            if filters == {
                "reference_type": "Opportunity",
                "reference_name": "OPP-1",
            }:
                return [SimpleNamespace(name="TODO-OPP")]

            return []

        with patch(
            "ai_sales_agent.ai_sales_agent.utils.claim_engine.frappe.get_all",
            side_effect=fake_get_all,
        ):
            names = {
                todo.name
                for todo in _get_related_todos(handoff)
            }

        self.assertEqual(
            names,
            {"TODO-HANDOFF", "TODO-OPP"},
        )


if __name__ == "__main__":
    unittest.main()
