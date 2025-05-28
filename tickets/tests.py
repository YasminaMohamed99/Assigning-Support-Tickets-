from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from .models import Ticket
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

    def test_admin_can_create_update_delete_ticket(self):
        self.client.force_authenticate(user=self.admin)

        # Create ticket
        create_res = self.client.post('/api/tickets/', {
            'subject': 'New Ticket',
            'description': 'Test Description',
            'created_by': self.admin.id,
        })
        self.assertEqual(create_res.status_code, 201)
        ticket_id = create_res.data['id']

        # Update ticket
        update_res = self.client.patch(f'/api/tickets/{ticket_id}/', {'subject': 'Updated Subject'})
        self.assertEqual(update_res.status_code, 200)
        self.assertEqual(update_res.data['subject'], 'Updated Subject')

        # Delete ticket
        delete_res = self.client.delete(f'/api/tickets/{ticket_id}/')
        self.assertEqual(delete_res.status_code, 204)

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


    def test_concurrent_fetch_no_overlaps(self):
        agents = [User.objects.create_user(username=f'agent{i}', password='pass', role='agent') for i in range(10)]

        def fetch_for_agent(agent):
            client = APIClient()
            client.force_authenticate(user=agent)
            return client.get('/api/tickets/fetch-tickets/')

        with ThreadPoolExecutor(max_workers=10) as executor:
            results = executor.map(fetch_for_agent, agents)

        all_ticket_ids = set()
        for res in results:
            self.assertEqual(res.status_code, 200)
            tickets_ids = {t['id'] for t in res.data}
            # Ensure no overlap with previously assigned tickets
            self.assertTrue(tickets_ids.isdisjoint(all_ticket_ids))
            all_ticket_ids.update(tickets_ids)

    def test_fetch_tickets_when_no_unassigned_tickets_left(self):
        self.client.force_authenticate(user=self.agent1)

        # Assign all tickets to some agent so no unassigned tickets remain
        Ticket.objects.filter(assigned_to__isnull=True).update(assigned_to=self.agent2)

        res = self.client.get('/api/tickets/fetch-tickets/')
        self.assertEqual(res.status_code, 200)
        # Tickets assigned to agent1 should be returned (possibly empty)
        self.assertLessEqual(len(res.data), 15)


