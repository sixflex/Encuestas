from django import forms
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError

ROL_CHOICES = [
    ("Administrador", "Administrador"),
    ("dirección", "dirección"),
    ("depto", "depto"),
    ("jefe_cuadrilla", "jefe_cuadrilla"),
    ("territorial", "territorial"),
]

def validar_email_unico_ci(value):
    # Unicidad case-insensitive
    if User.objects.filter(email__iexact=value).exists():
        raise ValidationError("Ya existe un usuario con este correo (no distingue mayúsculas/minúsculas).")

class UsuarioCrearForm(forms.ModelForm):
    # Campos extra para password y rol
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(render_value=False),
        required=True,
        min_length=8,
        help_text="Mínimo 8 caracteres."
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(render_value=False),
        required=True
    )
    rol = forms.ChoiceField(choices=ROL_CHOICES, required=True, label="Rol (grupo)")

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "is_active", "is_staff"]
        widgets = {
            "is_active": forms.CheckboxInput(),
            "is_staff": forms.CheckboxInput(),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip()
        # Valida formato básico y unicidad CI
        if not email:
            raise ValidationError("El correo es obligatorio.")
        validar_email_unico_ci(email)
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Las contraseñas no coinciden.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        # set_password hace hashing seguro
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            # grupo/rol único
            user.groups.clear()
            group, _ = Group.objects.get_or_create(name=self.cleaned_data["rol"])
            user.groups.add(group)
        return user


class UsuarioEditarForm(forms.ModelForm):
    # Password opcional en edición
    password1 = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput(render_value=False),
        required=False,
        min_length=8,
        help_text="Déjalo en blanco si no deseas cambiarla."
    )
    password2 = forms.CharField(
        label="Confirmar nueva contraseña",
        widget=forms.PasswordInput(render_value=False),
        required=False
    )
    rol = forms.ChoiceField(choices=ROL_CHOICES, required=True, label="Rol (grupo)")

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "is_active", "is_staff"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Preseleccionar rol actual (si tiene)
        groups = list(self.instance.groups.values_list("name", flat=True))
        if groups:
            self.fields["rol"].initial = groups[0]

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip()
        if not email:
            raise ValidationError("El correo es obligatorio.")
        # Unicidad CI excluyendo al propio usuario
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Ya existe un usuario con este correo (no distingue mayúsculas/minúsculas).")
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 or p2:
            if not p1 or not p2:
                self.add_error("password2", "Debes completar ambas contraseñas si vas a cambiarla.")
            elif p1 != p2:
                self.add_error("password2", "Las contraseñas no coinciden.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        p1 = self.cleaned_data.get("password1")
        if p1:
            user.set_password(p1)
        if commit:
            user.save()
            # rol
            user.groups.clear()
            group, _ = Group.objects.get_or_create(name=self.cleaned_data["rol"])
            user.groups.add(group)
        return user
