from rest_framework import viewsets, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction
from .models import Ticket
from .serializers import TicketSerializer
from .permissions import IsAdmin, IsAgent
from rest_framework.permissions import IsAuthenticated

from .utils import assign_tickets_to_agent


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        elif self.action in ['retrieve', 'list', 'fetch_tickets', 'sell_ticket']:
            return [IsAgent()]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        if user.role == 'agent':
            return Ticket.objects.filter(assigned_to=user)
        return super().get_queryset()

    @action(detail=False, methods=['get'], url_path='fetch-tickets')
    def fetch_tickets(self, request):
        user = request.user
        if user.role != 'agent':
            return Response({"detail": "Not authorized."}, status=403)

        tickets = assign_tickets_to_agent(user)
        serializer = self.get_serializer(tickets, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='sell')
    def sell_ticket(self, request, pk=None):
        ticket = self.get_object()

        if ticket.assigned_to != request.user:
            return Response({"detail": "Unauthorized"}, status=403)

        if ticket.is_sold:
            return Response({"detail": "Ticket already sold."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            ticket.is_sold = True
            ticket.save(update_fields=['is_sold', 'updated_at'])

        return Response({"detail": "Ticket marked as sold."}, status=status.HTTP_200_OK)

