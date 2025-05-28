from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Ticket

class TicketAssignmentTests(TestCase):
    def setUp(self):
        self.agent = get_user_model().objects.create_user(username='agent', password='test', role='agent')
        for i in range(50):
            Ticket.objects.create(subject=f"Test {i}", description="desc")

    def test_assign_15_tickets(self):
        self.client.login(username='agent', password='test')
        res = self.client.get('/api/tickets/fetch_tickets/')
        self.assertEqual(len(res.json()), 15)

    def test_no_duplicate_assignment(self):
        # simulate two agents
        agent2 = get_user_model().objects.create_user(username='agent2', password='test', role='agent')
        self.client.login(username='agent', password='test')
        res1 = self.client.get('/api/tickets/fetch_tickets/')
        self.client.logout()

        self.client.login(username='agent2', password='test')
        res2 = self.client.get('/api/tickets/fetch_tickets/')

        ids1 = {t['id'] for t in res1.json()}
        ids2 = {t['id'] for t in res2.json()}

        self.assertTrue(ids1.isdisjoint(ids2))

