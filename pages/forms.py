from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        input_class = "mt-1 w-full rounded-md border border-sendaoroi-gray/40 bg-white px-3 py-2 text-sm text-sendaoroi-blue focus:border-sendaoroi-green focus:outline-none focus:ring-2 focus:ring-sendaoroi-green/30"
        self.fields["name"].widget.attrs.update({"class": input_class})
        self.fields["email"].widget.attrs.update({"class": input_class})
        self.fields["phone"].widget.attrs.update({"class": input_class})
        self.fields["preferred_contact_method"].widget.attrs.update({"class": input_class})
        self.fields["message"].widget.attrs.update({"class": input_class})
        self.fields["privacy_accepted"].widget.attrs.update({"class": "h-4 w-4 rounded border-sendaoroi-gray/40 text-sendaoroi-blue focus:ring-sendaoroi-green"})

    class Meta:
        model = ContactMessage
        fields = [
            "name",
            "email",
            "phone",
            "preferred_contact_method",
            "message",
            "privacy_accepted",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={"placeholder": "Nombre"}
            ),
            "email": forms.EmailInput(
                attrs={"placeholder": "Email"}
            ),
            "phone": forms.TextInput(
                attrs={"placeholder": "Telefono"}
            ),
            "preferred_contact_method": forms.Select(),
            "message": forms.Textarea(
                attrs={"rows": 5, "placeholder": "Mensaje"}
            ),
        }
        labels = {
            "name": "Nombre",
            "email": "Email",
            "phone": "Telefono",
            "preferred_contact_method": "Preferencia de contacto",
            "message": "Mensaje",
            "privacy_accepted": "Acepto que Sendaoroi utilice estos datos únicamente para responder a mi consulta.",
        }

    def clean_privacy_accepted(self) -> bool:
        accepted = self.cleaned_data["privacy_accepted"]
        if not accepted:
            raise forms.ValidationError("Debes aceptar la política de privacidad para continuar.")
        return accepted
