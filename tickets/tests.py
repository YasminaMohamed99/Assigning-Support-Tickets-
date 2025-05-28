from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from .models import Ticket
from django.utils import timezone
from concurrent.futures import ThreadPoolExecutor

User = get_user_model()


class TicketAssignmentTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin', password='adminpass', role='admin')
        self.agent1 = User.objects.create_user(username='agent1', password='agentpass', role='agent')
        self.agent2 = User.objects.create_user(username='agent2', password='agentpass', role='agent')

        # Create 30 unassigned tickets by admin
        for i in range(30):
            Ticket.objects.create(subject=f"Ticket {i}", description="desc", created_by=self.admin)

        self.client = APIClient()

    def test_fetch_tickets_assigns_max_15(self):
        self.client.force_authenticate(user=self.agent1)
        response = self.client.get('/api/tickets/fetch-tickets/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 15)
        self.assertTrue(all(t['assigned_to'] is not None for t in response.data))

    def test_no_duplicate_ticket_assignments(self):
        def fetch_for_agent(agent):
            client = APIClient()
            client.force_authenticate(user=agent)
            return client.get('/api/tickets/fetch-tickets/')

        # Run both agents concurrently to test race conditions
        with ThreadPoolExecutor(max_workers=2) as executor:
            res1 = executor.submit(fetch_for_agent, self.agent1).result()
            res2 = executor.submit(fetch_for_agent, self.agent2).result()

        ids_agent1 = {t['id'] for t in res1.data}
        ids_agent2 = {t['id'] for t in res2.data}

        self.assertTrue(ids_agent1.isdisjoint(ids_agent2), "Agents received overlapping tickets")

    def test_fetch_more_than_once_returns_same_tickets(self):
        self.client.force_authenticate(user=self.agent1)
        res1 = self.client.get('/api/tickets/fetch-tickets/')
        res2 = self.client.get('/api/tickets/fetch-tickets/')

        ids1 = {t['id'] for t in res1.data}
        ids2 = {t['id'] for t in res2.data}

        self.assertSetEqual(ids1, ids2)

    def test_admin_cannot_fetch_tickets(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/tickets/fetch-tickets/')
        self.assertEqual(response.status_code, 403)
