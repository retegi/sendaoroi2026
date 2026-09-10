import time
from unittest.mock import patch

from django.core import mail
from django.core.cache import cache
from django.core.signing import dumps
from django.test import Client, TestCase, override_settings

from .models import ContactMessage


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