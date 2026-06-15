import logging

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import FormView, TemplateView

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

    def form_valid(self, form):
        contact_message = form.save()
        contact_recipient = getattr(settings, "CONTACT_RECIPIENT_EMAIL", None)
        default_from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "Sendaoroi <info@sendaoroi.org>")

        if contact_recipient:
            email_message = EmailMessage(
                subject=f"Nuevo mensaje desde Sendaoroi: {contact_message.name}",
                body=(
                    f"Nombre: {contact_message.name}\n"
                    f"Email: {contact_message.email}\n"
                    f"Teléfono: {contact_message.phone}\n"
                    f"Preferencia: {contact_message.get_preferred_contact_method_display()}\n\n"
                    f"Mensaje:\n{contact_message.message}"
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
                        "Gracias por escribirnos. Hemos recibido tu mensaje y te responderemos con el mayor cuidado posible."
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
