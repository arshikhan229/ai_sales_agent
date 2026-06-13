import frappe
import unittest

from ai_sales_agent.ai_sales_agent.workforce import workforce_dashboard


class TestWorkforceManagement(unittest.TestCase):

    def test_workforce_metrics_structure(self):
        data = workforce_dashboard.get_workforce_metrics()
        self.assertIsInstance(data, dict)
        self.assertIn('total_assigned_handoffs', data)

    def test_agent_performance_list(self):
        lst = workforce_dashboard.get_agent_performance()
        self.assertIsInstance(lst, list)

    def test_leaderboard_list(self):
        lb = workforce_dashboard.get_supervisor_leaderboard(limit=5)
        self.assertIsInstance(lb, list)


if __name__ == '__main__':
    unittest.main()
