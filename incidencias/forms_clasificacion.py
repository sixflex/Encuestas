from django import forms
from core.models import  TipoIncidencia, PreguntaBase
import re
from django.core.exceptions import ValidationError


class TipoIncidenciaForm(forms.ModelForm):
    class Meta:
        model = TipoIncidencia
        fields = ['nombre_problema', 'descripcion', 'tipo_gravedad']
        widgets = {
            'nombre_problema': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tipo_gravedad': forms.RadioSelect(attrs={'class': 'form-check-input'}),
        }

    def clean_nombre_problema(self):
        nombre = self.cleaned_data.get("nombre_problema", "").strip()

        if not nombre:
            raise ValidationError("El nombre del problema es obligatorio.")

        if nombre.isdigit():
            raise ValidationError("El nombre no puede ser solo números.")

        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ ]+$', nombre):
            raise ValidationError("El nombre solo puede contener letras y espacios.")

        return nombre

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get("descripcion", "").strip()

        if not descripcion:
            raise ValidationError("La descripción es obligatoria.")

        if descripcion.isdigit():
            raise ValidationError("La descripción no puede ser solo números.")
        if not re.match(r'^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ¡!¿?\.,;:\-()"\'# ]+$', descripcion):
            raise ValidationError("La descripción contiene caracteres no válidos.")

        return descripcion
    
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

    def clean_texto_pregunta(self):
        texto = self.cleaned_data.get("texto_pregunta", "").strip()

        if not texto:
            raise ValidationError("La pregunta es obligatoria.")

        if texto.isdigit():
            raise ValidationError("La pregunta no puede ser solo números.")

        if "?" not in texto and "¿" not in texto:
            raise ValidationError("La pregunta debe contener un signo de interrogación.")

        if not re.match(r'^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ¡!¿?\.,;:\-()"\'# ]+$', texto):
            raise ValidationError("La pregunta contiene caracteres no válidos.")

        return texto