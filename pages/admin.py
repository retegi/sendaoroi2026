from django.contrib import admin

from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "preferred_contact_method", "is_read", "created_at")
    list_filter = ("is_read", "preferred_contact_method")
    search_fields = ("name", "email", "phone", "message")
    readonly_fields = ("created_at",)
    actions = ("mark_as_read",)
    ordering = ("-created_at",)

    @admin.action(description="Marcar seleccionados como leidos")
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
