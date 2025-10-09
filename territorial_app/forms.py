from django import forms
from core.models import Incidencia, JefeCuadrilla
from registration.models import Profile

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
        fields = ['departamento','cuadrilla']
        widgets = {
            'departamento': forms.Select(attrs={'class': 'form-control'}),
            'cuadrilla': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Mostrar solo perfiles cuyo usuario pertenece al grupo "jefe de Cuadrilla" y está activo
        self.fields['cuadrilla'].queryset = Profile.objects.filter(
            user__groups__name__iexact="Jefe de Cuadrilla",
            user__is_active=True
        )
        