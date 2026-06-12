import frappe
from ai_sales_agent.ai_sales_agent.utils.handoff_rules import create_handoff
from ai_sales_agent.ai_sales_agent.utils.followup_tracker import record_followup, update_followup_metrics
from ai_sales_agent.ai_sales_agent.utils.sla_monitor import calculate_sla


def run():
    """Bench-executable smoke test.

    Usage:
      bench --site site1.local execute "import importlib; importlib.import_module('ai_sales_agent.ai_sales_agent.tests.test_followup_tracking').run()"
    """
    try:
        leads = frappe.get_all('AI Lead', limit=1, fields=['name'])
        if not leads:
            print('No AI Lead found on site — please run tests in a non-production environment with sample data.')
            return

        lead = leads[0].get('name')
        contact = frappe.db.get_value('AI Lead', lead, 'contact') or ''
        opportunity = frappe.db.get_value('AI Lead', lead, 'opportunity') or ''

        channel = 'Email'
        conversation = None

        print(f'Using lead={lead} contact={contact} opportunity={opportunity}')

        handoff_name = create_handoff(lead, contact, channel, conversation, opportunity, {})
        print('Handoff:', handoff_name)

        if not handoff_name:
            print('No handoff created — aborting test')
            return

        # Record a follow-up
        res = record_followup(handoff_name)
        print('Record followup:', res)

        # Recalculate metrics
        res2 = update_followup_metrics(handoff_name)
        print('Update metrics:', res2)

        # Get SLA
        hdoc = frappe.get_doc('AI Handoff', handoff_name)
        print('SLA:', calculate_sla(hdoc))

        print('Done')
    except Exception as e:
        print('Test failed:', e)
