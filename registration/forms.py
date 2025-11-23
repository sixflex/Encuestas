                                            

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from .models import Profile


                                                                                      
username_validator = RegexValidator(
    regex=r'^[\w.@+-]+$',
    message='El nombre de usuario sólo puede contener letras, números y @/./+/-/_'
)

                                                                 
phone_validator = RegexValidator(
    regex=r'^\+?\d{7,15}$',
    message='Teléfono inválido. Use formato +569XXXXXXXX o sólo dígitos (7-15 caracteres).'
)

class UserCreationFormWithEmail(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Requerido, 254 caracteres como máximo y debe ser válido")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Correo existe, prueba con otro")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
                         
        if len(username) < 3:
            raise ValidationError('El nombre de usuario debe tener al menos 3 caracteres.')
                
        username_validator(username)
                                     
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError('El nombre de usuario ya existe.')
        return username

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if password1:
            try:
                                                                     
                validate_password(password1, user=None)
            except ValidationError as e:
                raise forms.ValidationError(e.messages)
        return password1

    def clean(self):
        cleaned = super().clean()
        username = cleaned.get('username')
        email = cleaned.get('email')
        if username and email:
            local = email.split('@')[0]
            if username.lower() == local.lower():
                raise ValidationError('El nombre de usuario no puede ser la parte local del correo.')
        return cleaned


class ProfileForm(forms.ModelForm):
    telefono = forms.CharField(required=False, validators=[phone_validator])
    cargo = forms.CharField(required=False)

    class Meta:
        model = Profile
        fields = ['telefono', 'cargo']

    def clean_cargo(self):
        cargo = self.cleaned_data.get('cargo', '').strip()
        if cargo and len(cargo) < 3:
            raise ValidationError('El cargo debe tener al menos 3 caracteres.')
        return cargo

class EmailForm(forms.ModelForm):
    email = forms.EmailField(required=True, help_text="Requerido, 254 caracteres como máximo y debe ser válido")

    class Meta:
        model = User
        fields = ['email']        

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if 'email' in self.changed_data:
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("Correo existe, prueba con otro")
        return email

