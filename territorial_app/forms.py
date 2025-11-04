from django import forms
from core.models import Incidencia, JefeCuadrilla, Departamento, Encuesta
from registration.models import Profile
from django.forms import formset_factory
from core.models import Incidencia, JefeCuadrilla, Departamento, Encuesta, TipoIncidencia, PreguntaEncuesta

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
    """
    Formulario para crear/editar encuestas.
    - Agrega campo tipo_incidencia.
    - Opción para copiar preguntas default del tipo al crear una encuesta.
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

    # Campo no-modelo para decidir si clonar preguntas default al crear
    agregar_preguntas_default = forms.BooleanField(
        required=False,
        initial=True,
        label="Agregar preguntas por defecto del tipo seleccionado",
        help_text="Si está marcado, al crear la encuesta se copiarán automáticamente las preguntas por defecto del tipo de incidencia."
    )

    # Puedes declarar tipo_incidencia explícito si quieres personalizar el widget
    tipo_incidencia = forms.ModelChoiceField(
        queryset=TipoIncidencia.objects.all(),
        required=False,   # ponlo True si quieres forzarlo
        label="Tipo de Incidencia",
        widget=forms.Select()
    )

    class Meta:
        model = Encuesta
        fields = [
            'titulo', 'descripcion', 'ubicacion',
            'prioridad', 'departamento', 'estado',
            'tipo_incidencia',  # 🔹 importante
        ]
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
            'tipo_incidencia': forms.Select(),  # 🔹 widget explícito
        }
        labels = {
            'titulo': 'Título',
            'descripcion': 'Descripción',
            'ubicacion': 'Ubicación',
            'prioridad': 'Prioridad',
            'departamento': 'Departamento',
            'estado': 'Activa',
            'tipo_incidencia': 'Tipo de Incidencia',  # 🔹 label
        }
        help_texts = {
            'estado': 'Marcar si la encuesta está activa',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo departamentos activos
        self.fields['departamento'].queryset = Departamento.objects.filter(estado=True)

        # Valor por defecto de prioridad si no viene seteado
        if not self.initial.get('prioridad'):
            self.fields['prioridad'].initial = 'Normal'

        # Si quieres forzar que SIEMPRE se elija un tipo, cambia required=True arriba
        # y aquí puedes ajustar queryset si hubiera filtrado por algún criterio.
        self.fields['tipo_incidencia'].queryset = TipoIncidencia.objects.all().order_by('nombre_problema')

    def save(self, commit=True):
        """
        Guarda la encuesta y, si corresponde, clona las preguntas default del tipo.
        """
        # Detectamos si es creación
        creating = self.instance.pk is None

        # Guardamos la encuesta primero
        encuesta = super().save(commit=commit)

        # Si es creación y está marcado agregar preguntas default
        if creating and self.cleaned_data.get('agregar_preguntas_default'):
            tipo = self.cleaned_data.get('tipo_incidencia')
            if tipo:
                # Evitar duplicar si por algún motivo ya hay preguntas
                if not PreguntaEncuesta.objects.filter(encuesta=encuesta).exists():
                    defaults = PreguntaDefaultTipo.objects.filter(tipo_incidencia=tipo).order_by('orden', 'id')
                    objs = []
                    for p in defaults:
                        objs.append(PreguntaEncuesta(
                            texto_pregunta=p.texto_pregunta,
                            descripcion=p.descripcion,
                            tipo=p.tipo,
                            encuesta=encuesta
                        ))
                    if objs:
                        PreguntaEncuesta.objects.bulk_create(objs)

        return encuesta

# A) Form de Encuesta con "tipo_incidencia" incluido
class EncuestaConTipoForm(EncuestaForm):
    tipo_incidencia = forms.ModelChoiceField(
        queryset=TipoIncidencia.objects.all(),
        required=True,
        label="Tipo de Incidencia",
        widget=forms.Select()
    )

    class Meta(EncuestaForm.Meta):
        # anexamos el campo al listado de fields del form padre
        fields = EncuestaForm.Meta.fields + ['tipo_incidencia']


# B) Un form sencillo para una pregunta de encuesta (no ModelForm, porque aún no hay instancia)
class PreguntaSimpleForm(forms.Form):
    texto_pregunta = forms.CharField(label="Pregunta", max_length=200)
    tipo = forms.ChoiceField(
        label="Tipo de respuesta",
        choices=(
            ('texto', 'Texto'),
            ('numero', 'Número'),
            ('opcion', 'Opción'),
            ('fecha', 'Fecha'),
        )
    )
    descripcion = forms.CharField(
        label="Descripción (opcional)",
        required=False,
        widget=forms.Textarea(attrs={'rows': 2})
    )

# Formset para preguntas (lo llenaremos con initial de las default)
PreguntaFormSet = formset_factory(PreguntaSimpleForm, extra=0, can_delete=True)        
        self.fields['departamento'].queryset = Departamento.objects.filter(estado=True)
