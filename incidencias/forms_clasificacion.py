from django import forms
from core.models import  TipoIncidencia, PreguntaBase


class TipoIncidenciaForm(forms.ModelForm):
    class Meta:
        model = TipoIncidencia
        fields = ['nombre_problema', 'descripcion', 'tipo_gravedad']
        widgets = {
            'nombre_problema': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tipo_gravedad': forms.RadioSelect(attrs={'class': 'form-check-input'}),
        }
class PreguntaBaseForm(forms.ModelForm):
    class Meta:
        model = PreguntaBase
        fields = ['texto_pregunta', 'tipo']
        widgets = {
            'texto_pregunta': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'texto_pregunta': 'Texto de la pregunta',
            'tipo': 'Tipo de respuesta',
        }