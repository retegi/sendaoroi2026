from django.db import models
from django.utils.translation import gettext_lazy as _


class ContactMessage(models.Model):
    class PreferredContactMethod(models.TextChoices):
        EMAIL = "email", _("Email")
        PHONE = "phone", _("Telefono")
        WHATSAPP = "whatsapp", _("WhatsApp")
        TELEGRAM = "telegram", _("Telegram")
        SMS = "sms", _("SMS")

    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    preferred_contact_method = models.CharField(
        max_length=20,
        choices=PreferredContactMethod.choices,
    )
    message = models.TextField()
    privacy_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} - {self.created_at:%Y-%m-%d %H:%M}"
