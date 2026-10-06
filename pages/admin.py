from django import forms
from django.contrib import admin
from django.db import models
from django.utils.translation import gettext_lazy as _

from .models import (
    CollaboratingEntity,
    ContactMessage,
    LegalTexts,
    TeamGroup,
    TeamMember,
    TeamMembership,
)


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


@admin.register(LegalTexts)
class LegalTextsAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            _("Aviso legal"),
            {
                "fields": (
                    "legal_notice_es",
                    "legal_notice_eu",
                    "legal_notice_revision_date",
                    "legal_notice_published",
                )
            },
        ),
        (
            _("Privacidad"),
            {
                "fields": (
                    "privacy_es",
                    "privacy_eu",
                    "privacy_revision_date",
                    "privacy_published",
                )
            },
        ),
        (
            _("Cookies"),
            {
                "fields": (
                    "cookies_es",
                    "cookies_eu",
                    "cookies_revision_date",
                    "cookies_published",
                )
            },
        ),
        (_("Fechas del registro"), {"fields": ("created_at", "updated_at")}),
    )
    readonly_fields = ("created_at", "updated_at")
    formfield_overrides = {
        models.TextField: {
            "widget": forms.Textarea(attrs={"rows": 18, "cols": 100})
        }
    }

    def has_add_permission(self, request):
        return super().has_add_permission(request) and not LegalTexts.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


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
                    "organization_name",
                    "organization_logo",
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
