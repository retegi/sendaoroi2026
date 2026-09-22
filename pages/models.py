from django.conf import settings
from django.db import models
from django.utils.translation import get_language, gettext_lazy as _


def normalize_language_code(language_code=None):
    value = (language_code or get_language() or settings.LANGUAGE_CODE or "es").lower()
    code = value.split("-", 1)[0]
    if code in {"es", "eu"}:
        return code
    return "es"


def get_localized_value(language_code, value_es, value_eu):
    active_code = normalize_language_code(language_code)
    primary_value = value_es if active_code == "es" else value_eu
    secondary_value = value_eu if active_code == "es" else value_es
    for candidate in (primary_value, secondary_value):
        if candidate and candidate.strip():
            return candidate.strip()
    return primary_value or secondary_value or ""


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


class TeamGroup(models.Model):
    name_es = models.CharField(max_length=200, blank=True, default="")
    name_eu = models.CharField(max_length=200, blank=True, default="")
    description_es = models.TextField(blank=True, default="")
    description_eu = models.TextField(blank=True, default="")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "pk"]
        constraints = [
            models.CheckConstraint(check=models.Q(order__gte=0), name="teamgroup_order_non_negative"),
        ]

    def __str__(self):
        return self.get_name_for_language() or self.name_es or self.name_eu or f"TeamGroup {self.pk}"

    def get_name_for_language(self, language_code=None):
        return get_localized_value(language_code, self.name_es, self.name_eu)

    def get_description_for_language(self, language_code=None):
        return get_localized_value(language_code, self.description_es, self.description_eu)


class TeamMember(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="team_profile",
        null=True,
        blank=True,
    )
    photo = models.ImageField(upload_to="team/members/", blank=True, null=True)
    first_name = models.CharField(max_length=120, blank=True, default="")
    last_name_1 = models.CharField(max_length=120, blank=True, default="")
    last_name_2 = models.CharField(max_length=120, blank=True, default="")
    professional_role_es = models.CharField(max_length=200, blank=True, default="")
    professional_role_eu = models.CharField(max_length=200, blank=True, default="")
    description_es = models.TextField(blank=True, default="")
    description_eu = models.TextField(blank=True, default="")
    groups = models.ManyToManyField(
        "TeamGroup",
        through="TeamMembership",
        related_name="members",
        blank=True,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["first_name", "last_name_1", "last_name_2", "pk"]

    def __str__(self):
        if self.full_name:
            return self.full_name
        if self.user:
            if self.user.get_full_name():
                return self.user.get_full_name()
            return self.user.username or f"TeamMember {self.pk}"
        return f"TeamMember {self.pk}"

    @property
    def full_name(self):
        parts = [self.first_name.strip(), self.last_name_1.strip(), self.last_name_2.strip()]
        return " ".join(part for part in parts if part).strip()

    @property
    def has_photo(self):
        if not self.photo:
            return False
        try:
            return self.photo.storage.exists(self.photo.name)
        except Exception:
            return False

    @property
    def initials(self):
        letters = []
        for value in (self.first_name, self.last_name_1, self.last_name_2):
            if value and value.strip():
                letters.append(value.strip()[0].upper())
        if not letters:
            return ""
        return "".join(letters[:2])

    def get_role_for_language(self, language_code=None):
        return get_localized_value(language_code, self.professional_role_es, self.professional_role_eu)

    def get_description_for_language(self, language_code=None):
        return get_localized_value(language_code, self.description_es, self.description_eu)


class TeamMembership(models.Model):
    group = models.ForeignKey(
        TeamGroup,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    member = models.ForeignKey(
        TeamMember,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "pk"]
        constraints = [
            models.UniqueConstraint(fields=["group", "member"], name="unique_team_membership_per_group"),
            models.CheckConstraint(check=models.Q(order__gte=0), name="teammembership_order_non_negative"),
        ]

    def __str__(self):
        return f"{self.member} → {self.group}"


class CollaboratingEntity(models.Model):
    name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to="team/entities/", blank=True, null=True)
    description_es = models.TextField(blank=True, default="")
    description_eu = models.TextField(blank=True, default="")
    website = models.URLField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "pk"]
        constraints = [
            models.CheckConstraint(check=models.Q(order__gte=0), name="collaboratingentity_order_non_negative"),
        ]

    @property
    def has_logo(self):
        if not self.logo:
            return False
        try:
            return self.logo.storage.exists(self.logo.name)
        except Exception:
            return False

    def __str__(self):
        return self.name

    def get_description_for_language(self, language_code=None):
        return get_localized_value(language_code, self.description_es, self.description_eu)
