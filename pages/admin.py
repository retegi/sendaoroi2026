from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import CollaboratingEntity, ContactMessage, TeamGroup, TeamMember, TeamMembership


class TeamMembershipInline(admin.TabularInline):
    model = TeamMembership
    extra = 1
    fields = ("member", "order", "is_active")
    ordering = ("order", "pk")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "preferred_contact_method", "is_read", "created_at")
    list_filter = ("is_read", "preferred_contact_method")
    search_fields = ("name", "email", "phone", "message")
    readonly_fields = ("created_at",)
    actions = ("mark_as_read",)
    ordering = ("-created_at",)

    @admin.action(description=_("Marcar seleccionados como leidos"))
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)


@admin.register(TeamGroup)
class TeamGroupAdmin(admin.ModelAdmin):
    list_display = ("name_es", "name_eu", "order", "is_active")
    list_editable = ("order", "is_active")
    inlines = (TeamMembershipInline,)
    ordering = ("order", "pk")


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ("full_name", "professional_role_es", "professional_role_eu", "user", "is_active")
    list_editable = ("is_active",)
    list_filter = ("is_active",)
    search_fields = ("first_name", "last_name_1", "last_name_2", "professional_role_es", "professional_role_eu")
    fieldsets = (
        (
            _("Datos personales"),
            {
                "fields": (
                    "user",
                    "photo",
                    "first_name",
                    "last_name_1",
                    "last_name_2",
                    "is_active",
                )
            },
        ),
        (
            _("Cargo y descripción (Castellano)"),
            {"fields": ("professional_role_es", "description_es")},
        ),
        (
            _("Cargo y descripción (Euskara)"),
            {"fields": ("professional_role_eu", "description_eu")},
        ),
    )


@admin.register(CollaboratingEntity)
class CollaboratingEntityAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "is_active")
    list_editable = ("order", "is_active")
    ordering = ("order", "pk")
