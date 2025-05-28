from django.db import transaction
from django.utils import timezone
from .models import Ticket

def assign_tickets_to_agent(agent, max_tickets=15):
    """
    Assign up to max_tickets unassigned tickets to the agent,
    avoiding race conditions using select_for_update(skip_locked=True).
    Returns a queryset of assigned tickets.
    """

    with transaction.atomic():
        # Get tickets currently assigned to agent (not sold), limit max_tickets
        assigned_qs = Ticket.objects.select_for_update().filter(assigned_to=agent, is_sold=False).order_by('created_at', 'creation_order')[:max_tickets]
        assigned_tickets = list(assigned_qs)
        assigned_count = len(assigned_tickets)

        if assigned_count == max_tickets:
            return assigned_tickets

        needed = max_tickets - assigned_count

        unassigned_qs = Ticket.objects.select_for_update(skip_locked=True).filter(assigned_to__isnull=True, is_sold=False).order_by('created_at', 'creation_order')[:needed]
        now = timezone.now()
        ticket_ids = list(unassigned_qs.values_list('id', flat=True))

        if ticket_ids:
            Ticket.objects.filter(id__in=ticket_ids).update(assigned_to=agent, assigned_at=now, updated_at=now)
            unassigned_qs = Ticket.objects.filter(id__in=ticket_ids)

        all_tickets = assigned_tickets + list(unassigned_qs)
        all_tickets.sort(key=lambda t: (t.created_at, t.creation_order))
        return all_tickets[:max_tickets]

        # return list(Ticket.objects.filter(assigned_to=agent, is_sold=False).order_by('created_at')[:max_tickets])
