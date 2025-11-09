from django import forms
from core.models import Incidencia, JefeCuadrilla, Departamento, Encuesta, TipoIncidencia , PreguntaEncuesta
from registration.models import Profile
from django.forms import modelformset_factory

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

#------cambios barbara
#Solo temporal, hasta definir flujo de modulo de encuestas
class FinalizarIncidenciaForm(forms.ModelForm):
    observaciones = forms.CharField(
        label="Observaciones",
        widget=forms.Textarea(attrs={"rows": 3, "cols": 40}),
        max_length=500,
        required=False,
    )

    class Meta:
        model = Incidencia
        fields = ['observaciones']



class EncuestaForm(forms.ModelForm):
    tipo_incidencia = forms.ModelChoiceField(queryset=TipoIncidencia.objects.all(), widget=forms.Select(attrs={'class':'form-control'}))

    class Meta:
        model = Encuesta
        fields = ['titulo', 'descripcion', 'ubicacion', 'departamento', 'tipo_incidencia', 'estado']
        widgets = {
            'titulo': forms.TextInput(attrs={'class':'form-control'}),
            'descripcion': forms.Textarea(attrs={'class':'form-control', 'rows':3}),
            'ubicacion': forms.TextInput(attrs={'class':'form-control'}),
            'departamento': forms.Select(attrs={'class':'form-control'}),
            'estado': forms.CheckboxInput(),
        }

class PreguntaEncuestaForm(forms.Form):
    texto_pregunta = forms.CharField(label='Pregunta', widget=forms.TextInput(attrs={'class':'form-control'}))