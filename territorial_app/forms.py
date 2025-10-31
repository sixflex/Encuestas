from django import forms
from core.models import Incidencia, JefeCuadrilla, Encuesta, Departamento
from registration.models import Profile

class RechazarIncidenciaForm(forms.Form):
    motivo = forms.CharField(
        label="Motivo de rechazo",
        widget=forms.Textarea(attrs={"rows": 3, "cols": 40}),
        max_length=500,
        required=True,
    )

class ReasignarIncidenciaForm(forms.ModelForm):
    cuadrilla = forms.ModelChoiceField(
        queryset=JefeCuadrilla.objects.all(),
        required=True,
        label="Cuadrilla",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Incidencia
        fields = ['departamento', 'cuadrilla']
        widgets = {
            'departamento': forms.Select(attrs={'class': 'form-control'}),
        }


class EncuestaForm(forms.ModelForm):
    """
    Formulario para crear/editar encuestas.
    """
    PRIORIDAD_CHOICES = [
        ('Alta', 'Alta'),
        ('Normal', 'Normal'),
        ('Baja', 'Baja'),
    ]

    prioridad = forms.ChoiceField(
        choices=PRIORIDAD_CHOICES,
        required=True,
        label="Prioridad",
        widget=forms.Select()
    )

    class Meta:
        model = Encuesta
        fields = ['titulo', 'descripcion', 'ubicacion', 'prioridad', 'departamento', 'estado']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'placeholder': 'Título de la encuesta',
                'maxlength': '100'
            }),
            'descripcion': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Descripción detallada de la encuesta'
            }),
            'ubicacion': forms.TextInput(attrs={
                'placeholder': 'Ubicación de la encuesta',
                'maxlength': '200'
            }),
            'departamento': forms.Select(),
            'estado': forms.CheckboxInput(),
        }
        labels = {
            'titulo': 'Título',
            'descripcion': 'Descripción',
            'ubicacion': 'Ubicación',
            'prioridad': 'Prioridad',
            'departamento': 'Departamento',
            'estado': 'Activa',
        }
        help_texts = {
            'estado': 'Marcar si la encuesta está activa',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo departamentos activos
        self.fields['departamento'].queryset = Departamento.objects.filter(estado=True)