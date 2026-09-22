import os
import tempfile
import time
from unittest.mock import patch

from django.core import mail
from django.core.cache import cache
from django.core.management import call_command
from django.core.signing import dumps
from django.db import IntegrityError
from django.test import Client, TestCase, override_settings
from django.utils import translation

from .models import ContactMessage, CollaboratingEntity, TeamGroup, TeamMember, TeamMembership


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    TURNSTILE_SITE_KEY="test-site-key",
    TURNSTILE_SECRET_KEY="test-secret-key",
    CONTACT_RECIPIENT_EMAIL="info@sendaoroi.org",
    CONTACT_FORM_MIN_SECONDS=3,
    CONTACT_FORM_RATE_LIMIT_MAX=5,
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    },
)
class ContactFormSecurityTests(TestCase):
    url = "/es/contactar/"

    def setUp(self):
        cache.clear()

    def signed_timestamp(self, age=4):
        return dumps(time.time() - age, salt="sendaoroi.contact-form.timestamp")

    def payload(self, **overrides):
        data = {
            "name": "Ane Test",
            "email": "ane@example.com",
            "phone": "600000000",
            "preferred_contact_method": "email",
            "message": "Mezu bat bidali nahi dut.",
            "privacy_accepted": "on",
            "website": "",
            "contact_form_started": self.signed_timestamp(),
            "cf-turnstile-response": "valid-token",
        }
        data.update(overrides)
        return data

    @patch("pages.views.verify_turnstile", return_value=True)
    def test_valid_human_sends_email(self, verify):
        response = self.client.post(self.url, self.payload())

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(ContactMessage.objects.count(), 1)
        verify.assert_called_once()

    @patch("pages.views.verify_turnstile", return_value=True)
    def test_honeypot_does_not_send_or_store(self, verify):
        response = self.client.post(self.url, self.payload(website="bot value"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(ContactMessage.objects.count(), 0)
        verify.assert_not_called()

    @patch("pages.views.verify_turnstile", return_value=True)
    def test_timestamp_too_fast_does_not_send(self, verify):
        response = self.client.post(self.url, self.payload(contact_form_started=self.signed_timestamp(age=0)))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
        verify.assert_not_called()

    @patch("pages.views.verify_turnstile", return_value=True)
    def test_invalid_timestamp_does_not_send(self, verify):
        response = self.client.post(self.url, self.payload(contact_form_started="invalid"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
        verify.assert_not_called()

    @patch("pages.views.verify_turnstile", return_value=False)
    def test_invalid_turnstile_does_not_send(self, verify):
        response = self.client.post(self.url, self.payload())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(ContactMessage.objects.count(), 0)
        verify.assert_called_once()

    @patch("pages.views.verify_turnstile", return_value=True)
    def test_valid_turnstile_allows_email(self, verify):
        self.client.post(self.url, self.payload())

        self.assertEqual(len(mail.outbox), 1)
        verify.assert_called_once()

    @patch("pages.views.verify_turnstile", return_value=True)
    def test_invalid_email_does_not_send(self, verify):
        response = self.client.post(self.url, self.payload(email="not-an-email"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
        verify.assert_not_called()

    @patch("pages.views.verify_turnstile", return_value=True)
    def test_message_too_long_does_not_send(self, verify):
        response = self.client.post(self.url, self.payload(message="x" * 10001))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
        verify.assert_not_called()

    @override_settings(CONTACT_FORM_RATE_LIMIT_MAX=1)
    @patch("pages.views.verify_turnstile", return_value=True)
    def test_rate_limit_blocks_after_limit(self, verify):
        self.client.post(self.url, self.payload())
        response = self.client.post(self.url, self.payload())

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(verify.call_count, 1)

    @patch("pages.views.verify_turnstile", return_value=True)
    def test_email_uses_own_from_and_user_reply_to(self, verify):
        self.client.post(self.url, self.payload())

        sent_message = mail.outbox[0]
        self.assertEqual(sent_message.from_email, "Sendaoroi <info@sendaoroi.org>")
        self.assertEqual(sent_message.to, ["info@sendaoroi.org"])
        self.assertEqual(sent_message.reply_to, ["ane@example.com"])


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
        },
    }
)
class TeamContentTests(TestCase):
    def setUp(self):
        self.group_2 = TeamGroup.objects.create(
            name_es="Grupo de trabajo del programa",
            name_eu="Programa lan taldea",
            description_es="Primer grupo",
            description_eu="Lehenengo taldea",
            order=2,
            is_active=True,
        )
        self.group_1 = TeamGroup.objects.create(
            name_es="Grupo de psicólogas",
            name_eu="Psikologak",
            description_es="Segundo grupo",
            description_eu="Bigarren taldea",
            order=1,
            is_active=True,
        )
        self.inactive_group = TeamGroup.objects.create(
            name_es="Grupo inactivo",
            name_eu="Talde ez-aktiboa",
            order=3,
            is_active=False,
        )

        self.member_1 = TeamMember.objects.create(
            first_name="Ana",
            last_name_1="López",
            last_name_2="",
            professional_role_es="Psicóloga",
            professional_role_eu="Psikologa",
            description_es="Descripción castellana",
            description_eu="Deskribapen euskara",
            is_active=True,
        )
        self.member_2 = TeamMember.objects.create(
            first_name="Begoña",
            last_name_1="Sanz",
            last_name_2="Iriarte",
            professional_role_es="Coordinadora",
            professional_role_eu="Koordinatzailea",
            description_es="Otra descripción",
            description_eu="Beste deskribapena",
            is_active=True,
        )
        self.member_inactive = TeamMember.objects.create(
            first_name="Carmen",
            last_name_1="Ruiz",
            professional_role_es="Inactiva",
            professional_role_eu="Ez-aktiboa",
            description_es="No visible",
            description_eu="Ez ikusten",
            is_active=False,
        )

        TeamMembership.objects.create(group=self.group_2, member=self.member_2, order=2, is_active=True)
        TeamMembership.objects.create(group=self.group_2, member=self.member_1, order=1, is_active=True)
        TeamMembership.objects.create(group=self.group_1, member=self.member_1, order=1, is_active=True)
        TeamMembership.objects.create(group=self.group_1, member=self.member_inactive, order=2, is_active=False)

        self.entity = CollaboratingEntity.objects.create(
            name="Ekimen Elkartea",
            description_es="Entidad colaboradora",
            description_eu="Kolaborazio-erakunde",
            website="https://www.ekimen.eus",
            order=2,
            is_active=True,
        )
        CollaboratingEntity.objects.create(
            name="Entidad inactiva",
            description_es="No visible",
            description_eu="Ez ikusten",
            order=1,
            is_active=False,
        )

    def test_group_and_member_ordering(self):
        active_groups = list(
            TeamGroup.objects.filter(pk__in=[self.group_1.pk, self.group_2.pk]).order_by("order", "pk")
        )
        self.assertEqual(active_groups, [self.group_1, self.group_2])
        memberships = list(TeamMembership.objects.filter(group=self.group_2).order_by("order", "pk"))
        self.assertEqual([m.member_id for m in memberships], [self.member_1.id, self.member_2.id])

    def test_member_can_belong_to_multiple_groups(self):
        self.assertEqual(self.member_1.groups.count(), 2)

    def test_member_cannot_repeat_in_same_group(self):
        with self.assertRaises(IntegrityError):
            TeamMembership.objects.create(group=self.group_1, member=self.member_1, order=3, is_active=True)

    def test_locale_fallback_and_variants(self):
        self.assertEqual(self.member_1.get_role_for_language("es"), "Psicóloga")
        self.assertEqual(self.member_1.get_role_for_language("eu"), "Psikologa")
        self.assertEqual(self.member_1.get_role_for_language("es-es"), "Psicóloga")
        self.assertEqual(self.member_1.get_role_for_language("eu-es"), "Psikologa")
        self.member_1.professional_role_eu = ""
        self.member_1.save(update_fields=["professional_role_eu"])
        self.assertEqual(self.member_1.get_role_for_language("eu"), "Psicóloga")

    def test_full_name_and_initials_without_photo(self):
        self.assertEqual(self.member_1.full_name, "Ana López")
        self.assertEqual(self.member_1.initials, "AL")

    def test_public_team_page_only_shows_active_content(self):
        response = self.client.get("/es/equipo/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Grupo de psicólogas")
        self.assertContains(response, "Ekimen Elkartea")
        self.assertNotContains(response, "Grupo inactivo")
        self.assertNotContains(response, "Entidad inactiva")
        self.assertNotContains(response, "Carmen Ruiz")

    def test_team_page_uses_active_language_and_fallback_content(self):
        self.member_2.description_es = ""
        self.member_2.description_eu = "Deskribapen euskara bakarrik"
        self.member_2.save(update_fields=["description_es", "description_eu"])

        with translation.override("eu"):
            self.assertEqual(self.member_2.get_description_for_language(), "Deskribapen euskara bakarrik")
        with translation.override("es"):
            self.assertEqual(self.member_2.get_description_for_language(), "Deskribapen euskara bakarrik")

    def test_entity_description_and_web_url_are_safe(self):
        self.assertEqual(self.entity.get_description_for_language(), "Entidad colaboradora")
        self.assertEqual(self.entity.website, "https://www.ekimen.eus")