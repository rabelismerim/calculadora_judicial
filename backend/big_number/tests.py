from core.abstract.tests import AbstractTest
from creditors.models import Creditor
from projects.models import Project


class BigNumberDashboardTest(AbstractTest):
    """
    Test class for testing the API endpoints related to big numbers dashboard.
    """
    path = 'big_number/dashboard/'

    def test_api_get_dashboard(self):
        """
        Test method to check if API endpoint for getting dashboard data is working correctly.

        """
        response = super().test_api_get()
        dashboard = response.content
        self.assertEqual(len(dashboard['range_for_month']), 12)  # The default is to see the last 12 months
        self.assertEqual(len(dashboard['range_for_days']), 7)  # The default is to see the last 7 days
        self.assertSetEqual(set(dashboard['by_phase'].keys()),
                            {'adm', 'judicial'})  # The default is to see the adm and judicial count


class BigNumberProjectTest(AbstractTest):
    """
    Test class for testing the API endpoints related to big numbers dashboard.
    """
    project = Project.objects.first()
    path = f'big_number/project/{project.id if project else None}'

    def test_api_get_project(self):
        """
        Test method to check if API endpoint for getting project data is working correctly.

        """
        response = super().test_api_get()
        dashboard = response.content
        self.assertSetEqual(set(dashboard.keys()),
                            {'total_classes_creditor', 'total_creditor', 'total_sum_creditors',
                             'by_step'})


class BigNumberCreditorTest(AbstractTest):
    """
    Test class for testing the API endpoints related to big numbers dashboard.
    """
    project = Creditor.objects.first()
    path = f'big_number/creditor/{project.id if project else None}'

    def test_api_get_creditor(self):
        """
        Test method to check if API endpoint for getting creditor data is working correctly.

        """
        response = super().test_api_get()
        dashboard = response.content
        self.assertSetEqual(set(dashboard.keys()), {'total'})
