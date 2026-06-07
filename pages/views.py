from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from .forms import ContactForm


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


class ContactView(FormView):
    template_name = "pages/contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("contact")

    def form_valid(self, form):
        contact_message = form.save()

        contact_email = getattr(settings, "CONTACT_EMAIL", "info@sendaoroi.org")
        default_from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "info@sendaoroi.org")
        email_host = getattr(settings, "EMAIL_HOST", "")

        if email_host:
            send_mail(
                subject=f"[Sendaoroi] Nuevo mensaje de {contact_message.name}",
                message=(
                    f"Nombre: {contact_message.name}\n"
                    f"Email: {contact_message.email}\n"
                    f"Telefono: {contact_message.phone}\n"
                    f"Preferencia: {contact_message.get_preferred_contact_method_display()}\n\n"
                    f"Mensaje:\n{contact_message.message}"
                ),
                from_email=default_from_email,
                recipient_list=[contact_email],
                fail_silently=True,
            )

        messages.success(
            self.request,
            "Gracias por escribirnos. Hemos recibido tu mensaje y te responderemos con el mayor cuidado posible.",
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            "No hemos podido enviar el mensaje. Revisa los campos o inténtalo de nuevo más tarde.",
        )
        return super().form_invalid(form)
