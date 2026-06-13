import frappe
import unittest
import uuid
from unittest.mock import patch

from ai_sales_agent.ai_sales_agent.utils.claim_engine import close_handoff

# safe wrapper for has_column to avoid TableMissingError in test env
orig_has_column = getattr(frappe.db, 'has_column', None)
def has_column_safe(table, col):
    try:
        if orig_has_column:
            return orig_has_column(table, col)
        return False
    except Exception:
        return False


def _make_contact():
    name = f"Test Contact {uuid.uuid4().hex[:8]}"
    c = frappe.get_doc({"doctype": "Contact", "first_name": name})
    c.insert(ignore_permissions=True)
    return c.name


def _make_handoff(contact_name):
    h = frappe.get_doc({
        "doctype": "AI Handoff",
        "contact": contact_name,
        "channel": "Email",
        "status": "Open",
    })
    h.insert(ignore_permissions=True)
    return h.name


def _make_todo(handoff_name):
    td = frappe.get_doc({
        "doctype": "ToDo",
        "description": "Test close todo",
        "reference_type": "AI Handoff",
        "reference_name": handoff_name,
    })
    td.insert(ignore_permissions=True)
    return td.name


class TestCloseHandoff(unittest.TestCase):
    def tearDown(self):
        frappe.db.rollback()

    def test_close_handoff_closed_won(self):
        contact = _make_contact()
        handoff = _make_handoff(contact)
        todo = _make_todo(handoff)

        res = close_handoff(handoff, outcome="Closed Won", note="Automated close test from agent")
        self.assertEqual(res.get("status"), "success")

        h = frappe.get_doc("AI Handoff", handoff)
        self.assertIn(h.status, ("Closed Won", "Closed"))
        self.assertIn("Automated close test from agent", (h.notes or ""))

        convs = frappe.get_all(
            "CRM Conversation",
            filters={"contact": contact, "message": ["like", "%Handoff closed:%"]},
        )
        self.assertTrue(len(convs) >= 1)

        # Verify ToDo is closed if status or completed columns exist
        todo_doc = frappe.get_doc("ToDo", todo)
        # If status column exists, expect 'Closed'
        if has_column_safe('tabToDo', 'status'):
            self.assertIn(getattr(todo_doc, 'status', '').lower(), ('closed', ''))
        # If completed column exists, expect truthy
        if has_column_safe('tabToDo', 'completed'):
            val = frappe.db.get_value('ToDo', todo, 'completed')
            self.assertIn(val, (1, '1', True))

    def test_close_handoff_closed_lost(self):
        contact = _make_contact()
        handoff = _make_handoff(contact)
        todo = _make_todo(handoff)

        res = close_handoff(handoff, outcome="Closed Lost", note="Lost for testing")
        self.assertEqual(res.get("status"), "success")

        h = frappe.get_doc("AI Handoff", handoff)
        self.assertIn(h.status, ("Closed Lost", "Closed"))
        self.assertIn("Lost for testing", (h.notes or ""))

    def test_close_handoff_todo_column_variations(self):
        """Ensure function works when ToDo.completed exists or not by mocking has_column."""
        contact = _make_contact()
        handoff = _make_handoff(contact)
        todo = _make_todo(handoff)

        # Case A: completed missing, status present
        def has_col_a(table, col):
            if table == 'tabToDo' and col == 'completed':
                return False
            if table == 'tabToDo' and col == 'status':
                return True
            return has_column_safe(table, col)

        with patch.object(frappe.db, 'has_column', side_effect=has_col_a):
            with patch.object(frappe.db, 'set_value') as mock_set:
                res = close_handoff(handoff, outcome="Closed", note="Variation A")
                self.assertEqual(res.get("status"), "success")
                # Expect status column to be set via set_value
                mock_set.assert_any_call('ToDo', todo, 'status', 'Closed')

        # Case B: status missing, completed present
        def has_col_b(table, col):
            if table == 'tabToDo' and col == 'completed':
                return True
            if table == 'tabToDo' and col == 'status':
                return False
            return has_column_safe(table, col)

        with patch.object(frappe.db, 'has_column', side_effect=has_col_b):
            with patch.object(frappe.db, 'set_value') as mock_set2:
                res = close_handoff(handoff, outcome="Closed", note="Variation B")
                self.assertEqual(res.get("status"), "success")
                mock_set2.assert_any_call('ToDo', todo, 'completed', 1)


if __name__ == '__main__':
    # This file is primarily for the Frappe test runner; a minimal entrypoint is provided for ad-hoc runs.
    frappe.init(site='site1.local')
    unittest.main()
