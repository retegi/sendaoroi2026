import logging

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import FormView, TemplateView

from .antispam import check_rate_limit, verify_turnstile
from .forms import ContactForm

logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    template_name = "pages/home.html"


class RootsView(TemplateView):
    template_name = "pages/roots.html"


class ProgramView(TemplateView):
    template_name = "pages/program.html"


class WhatWeDoView(TemplateView):
    template_name = "pages/what_we_do.html"


class CompassView(TemplateView):
    template_name = "pages/compass.html"


class ProcessView(TemplateView):
    template_name = "pages/process.html"


class ServicesView(TemplateView):
    template_name = "pages/services.html"


class IsItForMeView(TemplateView):
    template_name = "pages/is_it_for_me.html"


class TeamView(TemplateView):
    template_name = "pages/team.html"


class LegalNoticeView(TemplateView):
    template_name = "pages/legal_notice.html"


class PrivacyView(TemplateView):
    template_name = "pages/privacy.html"


class CookiesView(TemplateView):
    template_name = "pages/cookies.html"


class ContactView(FormView):
    template_name = "pages/contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("contact")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["turnstile_site_key"] = settings.TURNSTILE_SITE_KEY
        context["turnstile_required"] = bool(
            settings.TURNSTILE_SITE_KEY or settings.TURNSTILE_SECRET_KEY
        )
        return context

    def post(self, request, *args, **kwargs):
        if request.POST.get("website", "").strip():
            logger.info("contact_form_spam_blocked reason=honeypot")
            messages.success(
                request,
                _(
                    "Gracias. Hemos recibido tu mensaje correctamente y te responderemos lo antes posible."
                ),
            )
            return self.form_valid_without_sending()

        if not check_rate_limit(request):
            logger.info("contact_form_spam_blocked reason=rate_limit")
            messages.error(
                request,
                _("Has realizado demasiados intentos. Inténtalo de nuevo más tarde."),
            )
            return self.form_invalid_without_form()

        return super().post(request, *args, **kwargs)

    def form_valid_without_sending(self):
        return self.redirect_to_success()

    def form_invalid_without_form(self):
        return self.redirect_to_success()

    def redirect_to_success(self):
        from django.http import HttpResponseRedirect

        return HttpResponseRedirect(self.get_success_url())

    def form_valid(self, form):
        turnstile_token = self.request.POST.get("cf-turnstile-response", "")
        if not verify_turnstile(self.request, turnstile_token):
            logger.info("contact_form_spam_blocked reason=invalid_turnstile")
            form.add_error(
                None,
                _("No hemos podido verificar el formulario. Inténtalo de nuevo."),
            )
            return self.form_invalid(form)

        contact_message = form.save()
        contact_recipient = getattr(settings, "CONTACT_RECIPIENT_EMAIL", None)
        default_from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "Sendaoroi <info@sendaoroi.org>")

        if contact_recipient:
            email_message = EmailMessage(
                subject="Sendaoroiko kontaktu-mezu berria",
                body=(
                    f"Izena: {contact_message.name}\n"
                    f"Posta elektronikoa: {contact_message.email}\n"
                    f"Telefonoa: {contact_message.phone}\n"
                    f"Harremanetarako hobespena: {contact_message.get_preferred_contact_method_display()}\n\n"
                    f"Mezua:\n{contact_message.message}"
                ),
                from_email=default_from_email,
                to=[contact_recipient],
                reply_to=[contact_message.email] if contact_message.email else [],
            )

            try:
                email_message.send(fail_silently=False)
                messages.success(
                    self.request,
                    _(
                        "Gracias. Hemos recibido tu mensaje correctamente y te responderemos lo antes posible."
                    ),
                )
            except Exception:
                logger.exception("Error enviando email de contacto")
                messages.error(
                    self.request,
                    _(
                        "Hubo un problema al enviar tu mensaje. Por favor intenta de nuevo más tarde."
                    ),
                )
                return super().form_valid(form)
        else:
            logger.warning("No hay CONTACT_RECIPIENT_EMAIL configurado para el envío de emails de contacto")
            messages.error(
                self.request,
                _(
                    "No se ha podido enviar el mensaje porque falta una configuración de correo. Contacta con el administrador."
                ),
            )

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            _("No hemos podido enviar el mensaje. Revisa los campos o inténtalo de nuevo más tarde."),
        )
        return super().form_invalid(form)
