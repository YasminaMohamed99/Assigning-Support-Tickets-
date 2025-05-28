from django.contrib import admin
from .models import Ticket

class TicketAdmin(admin.ModelAdmin):
    list_display = ("id", "subject", "created_by", "assigned_to", "created_at", "updated_at", "creation_order")
    list_filter = ("assigned_to", "created_at")
    search_fields = ("subject", "description", "assigned_to__username")
    ordering = ("-created_at","-creation_order")

    # Optional: prevent non-admins from editing
    def has_change_permission(self, request, obj=None):
        if request.user.role != "admin":
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if request.user.role != "admin":
            return False
        return super().has_delete_permission(request, obj)

    def has_add_permission(self, request):
        return request.user.role == "admin"

admin.site.register(Ticket, TicketAdmin)
