from django import forms
from core.models import Incidencia, JefeCuadrilla, Departamento, Encuesta, TipoIncidencia, PreguntaEncuesta, Multimedia
from registration.models import Profile
from django.forms import modelformset_factory
from django.core.exceptions import ValidationError #ESTO SE USA PARA VALIDAR EL TAMAÑO Y TIPO DE ARCHIVO (nuevo)
from django.conf import settings #ESTO SE USA PARA ACCEDER A LAS CONFIGURACIONES DE SETTINGS.PY (nuevo)

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



# FORMULARIO DE EVIDENCIAS - NUEVO
class EvidenciaForm(forms.ModelForm):
    """Formulario para subir evidencias (imágenes, videos, audios, documentos)"""
    
    class Meta:
        model = Multimedia
        fields = ['nombre', 'archivo']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la evidencia (ej: "Foto del bache reparado")'
            }),
            'archivo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*,video/*,audio/*,.pdf,.doc,.docx',
                'id': 'inputArchivo'
            })
        }
        labels = {
            'nombre': 'Nombre descriptivo',
            'archivo': 'Seleccionar archivo'
        }
    
    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')
        
        if archivo:
            # Validar tamaño
            if archivo.size > settings.MAX_UPLOAD_SIZE:
                raise ValidationError(
                    f'El archivo es demasiado grande. Tamaño máximo: {settings.MAX_UPLOAD_SIZE / (1024*1024):.0f}MB'
                )
            
            # Obtener tipo de contenido
            content_type = archivo.content_type
            
            # Validar tipo de archivo
            allowed_types = (
                settings.ALLOWED_IMAGE_TYPES + 
                settings.ALLOWED_VIDEO_TYPES + 
                settings.ALLOWED_AUDIO_TYPES + 
                settings.ALLOWED_DOCUMENT_TYPES
            )
            
            if content_type not in allowed_types:
                raise ValidationError(
                    'Tipo de archivo no permitido. Formatos válidos: '
                    'imágenes (jpg, png, gif), videos (mp4, avi), '
                    'audios (mp3, wav), documentos (pdf, doc)'
                )
        
        return archivo
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Detectar tipo de archivo automáticamente
        archivo = self.cleaned_data.get('archivo')
        if archivo:
            content_type = archivo.content_type
            extension = archivo.name.split('.')[-1].lower()
            
            if content_type in settings.ALLOWED_IMAGE_TYPES:
                instance.tipo = 'imagen'
            elif content_type in settings.ALLOWED_VIDEO_TYPES:
                instance.tipo = 'video'
            elif content_type in settings.ALLOWED_AUDIO_TYPES:
                instance.tipo = 'audio'
            elif content_type in settings.ALLOWED_DOCUMENT_TYPES:
                instance.tipo = 'documento'
            else:
                instance.tipo = 'otro'
            
            instance.formato = extension
            instance.tamanio = archivo.size
        
        if commit:
            instance.save()
        
        return instance