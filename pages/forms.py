import time

from django import forms
from django.conf import settings
from django.core.signing import BadSignature, SignatureExpired, loads
from django.utils.translation import gettext_lazy as _

from .antispam import signed_form_timestamp
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    message = forms.CharField(
        max_length=10000,
        widget=forms.Textarea(attrs={"rows": 5, "placeholder": _("Mensaje")}),
    )
    website = forms.CharField(
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={
                "tabindex": "-1",
                "autocomplete": "off",
                "aria-hidden": "true",
                "style": "display:none",
            }
        ),
    )
    contact_form_started = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound:
            self.initial["contact_form_started"] = signed_form_timestamp()
        input_class = "mt-1 w-full rounded-md border border-sendaoroi-gray/40 bg-white px-3 py-2 text-sm text-sendaoroi-blue focus:border-sendaoroi-green focus:outline-none focus:ring-2 focus:ring-sendaoroi-green/30"
        self.fields["name"].widget.attrs.update({"class": input_class})
        self.fields["email"].widget.attrs.update({"class": input_class})
        self.fields["phone"].widget.attrs.update({"class": input_class})
        self.fields["preferred_contact_method"].widget.attrs.update({"class": input_class})
        self.fields["message"].widget.attrs.update({"class": input_class})
        self.fields["privacy_accepted"].widget.attrs.update({"class": "h-4 w-4 rounded border-sendaoroi-gray/40 text-sendaoroi-blue focus:ring-sendaoroi-green"})

    def clean_contact_form_started(self):
        signed_timestamp = self.cleaned_data["contact_form_started"]
        try:
            started_at = loads(
                signed_timestamp,
                salt=settings.CONTACT_FORM_TIMESTAMP_SALT,
                max_age=settings.CONTACT_FORM_TIMESTAMP_MAX_AGE,
            )
        except (BadSignature, SignatureExpired, TypeError, ValueError):
            raise forms.ValidationError(
                _("No hemos podido verificar el formulario. Inténtalo de nuevo.")
            )

        if not isinstance(started_at, (int, float)) or time.time() - started_at < settings.CONTACT_FORM_MIN_SECONDS:
            raise forms.ValidationError(
                _("No hemos podido verificar el formulario. Inténtalo de nuevo.")
            )
        return signed_timestamp

    def clean_website(self):
        website = self.cleaned_data["website"].strip()
        if website:
            raise forms.ValidationError(_("No hemos podido verificar el formulario."))
        return website

    class Meta:
        model = ContactMessage
        fields = [
            "name",
            "email",
            "phone",
            "preferred_contact_method",
            "message",
            "privacy_accepted",
            "website",
            "contact_form_started",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={"placeholder": _("Nombre")}
            ),
            "email": forms.EmailInput(
                attrs={"placeholder": _("Email")}
            ),
            "phone": forms.TextInput(
                attrs={"placeholder": _("Telefono")}
            ),
            "preferred_contact_method": forms.Select(),
            "message": forms.Textarea(
                attrs={"rows": 5, "placeholder": _("Mensaje")}
            ),
        }
        labels = {
            "name": _("Nombre"),
            "email": _("Email"),
            "phone": _("Telefono"),
            "preferred_contact_method": _("Preferencia de contacto"),
            "message": _("Mensaje"),
            "privacy_accepted": _("Acepto que Sendaoroi utilice estos datos únicamente para responder a mi consulta."),
        }

    def clean_privacy_accepted(self) -> bool:
        accepted = self.cleaned_data["privacy_accepted"]
        if not accepted:
            raise forms.ValidationError(_("Debes aceptar la política de privacidad para continuar."))
        return accepted
