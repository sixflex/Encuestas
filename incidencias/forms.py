#Incidencias/forms.py -> modificaciones cotta
from django import forms
from core.models import Incidencia, Departamento
from django.core.exceptions import ValidationError

class IncidenciaForm(forms.ModelForm):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('proceso', 'En proceso'),
        ('finalizada', 'Finalizada'),
        ('validada', 'Validada'),
        ('rechazada', 'Rechazada'),
    ]

    PRIORIDAD_CHOICES = [
        ('alta', 'Alta'),
        ('media', 'Media'),
        ('baja', 'Baja'),
    ]
    
    estado = forms.ChoiceField(
        choices=ESTADO_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        required=True,
        label="Estado"
    )

    prioridad = forms.ChoiceField(
        choices=PRIORIDAD_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        required=True,
        label="Prioridad"
    )

    class Meta:
        model = Incidencia
        fields = [
            "titulo", "descripcion", "estado", "prioridad", "fecha_cierre",
            "latitud", "longitud", "departamento"
        ]
        widgets = {
            "titulo": forms.TextInput(attrs={"class": "form-control", "placeholder": "Título"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "fecha_cierre": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
            "latitud": forms.NumberInput(attrs={"class": "form-control"}),
            "longitud": forms.NumberInput(attrs={"class": "form-control"}),
            "departamento": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo muestra departamentos activos
        self.fields['departamento'].queryset = Departamento.objects.filter(estado=True)
        # Hacer obligatorios algunos campos en el form
        self.fields['titulo'].required = True
        self.fields['descripcion'].required = True
        self.fields['departamento'].required = True

        # Valores por defecto sólo al crear (instance sin pk)
        if not self.instance or not getattr(self.instance, 'pk', None):
            # establecer valores iniciales
            self.fields['estado'].initial = 'pendiente'
            self.fields['prioridad'].initial = 'media'

    def clean_titulo(self):
        titulo = self.cleaned_data.get("titulo", "").strip()
        if not titulo:
            raise ValidationError("El título de la incidencia es obligatorio.")
        if Incidencia.objects.filter(titulo__iexact=titulo).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Ya existe una incidencia con este título.")
        return titulo

    def clean_estado(self):
        estado = self.cleaned_data.get("estado")
        if not estado:
            return "pendiente"
        return estado

    def clean_prioridad(self):
        prioridad = self.cleaned_data.get("prioridad")
        if not prioridad:
            return "media"
        return prioridad

    def save(self, commit=True):
        incidencia = super().save(commit=False)
        incidencia.titulo = incidencia.titulo.strip()
        if commit:
            incidencia.save()
        return incidencia


