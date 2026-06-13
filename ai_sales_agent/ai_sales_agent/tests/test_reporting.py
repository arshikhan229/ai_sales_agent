import frappe
import unittest

from ai_sales_agent.ai_sales_agent.reporting import reporting


class TestReportingAPIs(unittest.TestCase):
    def test_dashboard_metrics_keys(self):
        data = reporting.get_dashboard_metrics()
        self.assertIn('total_leads', data)
        self.assertIn('pipeline_value', data)

    def test_funnel_metrics(self):
        f = reporting.get_funnel_metrics()
        self.assertIn('lead', f)
        self.assertIn('won', f)

    def test_channel_metrics(self):
        c = reporting.get_channel_metrics()
        self.assertIn('whatsapp_leads', c)
        self.assertIn('conversion_per_channel', c)

    def test_agent_metrics_return_list(self):
        a = reporting.get_agent_metrics()
        self.assertIsInstance(a, list)

    def test_sla_metrics_return_map(self):
        s = reporting.get_sla_metrics()
        self.assertIsInstance(s, dict)


if __name__ == '__main__':
    unittest.main()
