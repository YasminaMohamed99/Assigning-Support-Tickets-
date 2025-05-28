from django.db import models
from django.conf import settings
from django.db.models import Max
from django.utils import timezone


class Ticket(models.Model):
    subject = models.CharField(max_length=255)
    description = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='created_tickets',limit_choices_to={'role': 'admin'},  null=True, blank=True)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, limit_choices_to={'role': 'agent'}, related_name='tickets')
    is_sold = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_at = models.DateTimeField(null=True, blank=True, db_index=True)
    creation_order = models.PositiveIntegerField(editable=False, db_index=True, unique=True)

    class Meta:
        ordering = ['created_at', 'creation_order']
        indexes = [models.Index(fields=['assigned_to', 'is_sold', 'created_at', 'creation_order'])]

    def save(self, *args, **kwargs):
        if not self.pk and not self.creation_order:
            max_order = Ticket.objects.aggregate(Max('creation_order'))['creation_order__max'] or 0
            self.creation_order = max_order + 1
        super().save(*args, **kwargs)

    def assign_to_agent(self, agent):
        self.assigned_to = agent
        self.assigned_at = timezone.now()
        self.save(update_fields=['assigned_to', 'assigned_at'])
