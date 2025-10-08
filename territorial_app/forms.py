from django import forms
from core.models import Incidencia

class RechazarIncidenciaForm(forms.Form):
    motivo = forms.CharField(
        label="Motivo de rechazo",
        widget=forms.Textarea(attrs={"rows": 3, "cols": 40}),
        max_length=500,
        required=True,
    )

class ReasignarIncidenciaForm(forms.ModelForm):
    class Meta:
        model = Incidencia
        fields = ['departamento', 'cuadrilla']
        widgets = {
            'departamento': forms.Select(attrs={'class': 'form-control'}),
            'cuadrilla': forms.Select(attrs={'class': 'form-control'}),
        }
