from django.db import models
from registration.models import Profile
from django.core.validators import FileExtensionValidator #ESTO SE USA PARA VALIDAR EXTENSIONES DE ARCHIVOS (NUEVO)

class Perfil(models.Model):
    rol = models.CharField(max_length=50)

    def __str__(self):
        return self.rol

class Direccion(models.Model):
    nombre_direccion = models.CharField(max_length=100)
    estado = models.BooleanField(default=True)
    creadoEl = models.DateTimeField(auto_now_add=True)
    actualizadoEl = models.DateTimeField(auto_now=True)
    encargado = models.ForeignKey(
        Profile, on_delete=models.SET_NULL, null=True, related_name='direcciones_encargadas'
    )

    def __str__(self):
        return self.nombre_direccion


class Departamento(models.Model):
    nombre_departamento = models.CharField(max_length=100)
    estado = models.BooleanField(default=True)
    creadoEl = models.DateTimeField(auto_now_add=True)
    actualizadoEl = models.DateTimeField(auto_now=True)
    encargado = models.ForeignKey(
        Profile, on_delete=models.SET_NULL, null=True, related_name='departamentos_encargados'
    )
    direccion = models.ForeignKey(Direccion, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.nombre_departamento


class Encuesta(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    ubicacion = models.CharField(max_length=200)
    estado = models.BooleanField(default=True)
    creadoEl = models.DateTimeField(auto_now_add=True)
    actualizadoEl = models.DateTimeField(auto_now=True)
    prioridad = models.CharField(max_length=50)
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE)
    tipo_incidencia = models.ForeignKey('TipoIncidencia', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.titulo


class PreguntaEncuesta(models.Model):
    texto_pregunta = models.CharField(max_length=200)
    descripcion = models.TextField()
    tipo = models.CharField(max_length=50, choices=[
            ('texto', 'Texto'),
            ('numero', 'Número'),
            ('opcion', 'Opción múltiple')
        ],
        default='texto'
    )
    encuesta = models.ForeignKey(Encuesta, on_delete=models.CASCADE)
    def __str__(self):
        return self.texto_pregunta


class RespuestaEncuesta(models.Model):
    texto_respuesta = models.TextField()
    tipo = models.CharField(max_length=50)
    pregunta = models.ForeignKey(PreguntaEncuesta, on_delete=models.CASCADE, 
        related_name='respuestas')

    def __str__(self):
        return self.texto_respuesta[:50]

class Multimedia(models.Model):
    TIPO_CHOICES = [
        ('imagen', 'Imagen'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('documento', 'Documento'),
        ('otro', 'Otro'),
    ]
    
    nombre = models.CharField(max_length=100)
    archivo = models.FileField(
        upload_to='evidencias/%Y/%m/%d/',
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    'jpg', 'jpeg', 'png', 'gif', 'webp',  # Imágenes
                    'mp4', 'mpeg', 'avi', 'mov',          # Videos
                    'mp3', 'wav', 'ogg', 'm4a',           # Audios
                    'pdf', 'doc', 'docx', 'txt'           # Documentos
                ]
            )
        ]
    )
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES)
    formato = models.CharField(max_length=50)
    tamanio = models.IntegerField(help_text="Tamaño en bytes", null=True, blank=True)
    creadoEl = models.DateTimeField(auto_now_add=True)
    incidencia = models.ForeignKey("Incidencia", on_delete=models.CASCADE, related_name="multimedias")
    encuesta = models.ForeignKey("Encuesta", on_delete=models.CASCADE, related_name="evidencias", 
                                 null=True, blank=True)

    class Meta:
        ordering = ['-creadoEl']
        verbose_name = 'Evidencia Multimedia'
        verbose_name_plural = 'Evidencias Multimedia'

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"
    
    def get_icono(self):
        """Retorna el icono a mostrar según el tipo de archivo"""
        iconos = {
            'imagen': '🖼️',
            'video': '🎥',
            'audio': '🎵',
            'documento': '📄',
            'otro': '📎'
        }
        return iconos.get(self.tipo, '📎')


class TipoIncidencia(models.Model):
    nombre_problema = models.CharField(max_length=100)
    descripcion = models.TextField()
    tipo_gravedad = models.CharField(
        max_length=1,
        choices=[('A', 'Alta'), ('M', 'Media'), ('B', 'Baja')]
    )

    def __str__(self):
        return self.nombre_problema


class JefeCuadrilla(models.Model):
    nombre_cuadrilla = models.CharField(max_length=100)
    encargado = models.ForeignKey(
        Profile, on_delete=models.SET_NULL, null=True, related_name='cuadrillas_encargadas'
    )
    departamento = models.ForeignKey(Departamento, on_delete=models.SET_NULL, null=True)
    usuario = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='cuadrillas'
    )

    def __str__(self):
        return self.nombre_cuadrilla

#-------------------------------------------------
class Incidencia(models.Model):
    #Cambios cotta
# 1. DEFINICIÓN DE CHOICES (Opciones de Estado)
    ESTADO_CHOICES = (
    ('Pendiente', 'Pendiente'),
    ('En Progreso', 'En Progreso'),
    ('Completada', 'Completada'),
    ('Rechazada', 'Rechazada'), 
    ('Validada', "Validada")
    )

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    #Cambios cotta
    #estado = models.CharField(max_length=50)
     # 2. CAMBIO CLAVE: Asignar el valor por defecto
    estado = models.CharField(
        max_length=50, choices=ESTADO_CHOICES, default='Pendiente')     # <--- ESTO MARCA EL VALOR POR DEFECTO
    #-----------------------------------------------------------
    prioridad = models.CharField(max_length=50)
    creadoEl = models.DateTimeField(auto_now_add=True)
    actualizadoEl = models.DateTimeField(auto_now=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    latitud = models.FloatField()
    longitud = models.FloatField()
    nombre_vecino = models.CharField(max_length=100)
    correo_vecino = models.EmailField()
    telefono_vecino = models.CharField(max_length=20)
    motivo_rechazo = models.TextField(null=True, blank=True)

    cuadrilla = models.ForeignKey(JefeCuadrilla, on_delete=models.SET_NULL, null=True)
    respuesta = models.ForeignKey(RespuestaEncuesta, on_delete=models.SET_NULL, null=True)
    departamento = models.ForeignKey(Departamento, on_delete=models.SET_NULL, null=True)
    encuesta = models.ForeignKey(Encuesta, on_delete=models.SET_NULL, null=True)
    tipo_incidencia = models.ForeignKey(TipoIncidencia, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.titulo


class Territorial(models.Model):
    incidencia = models.ForeignKey(
        Incidencia, on_delete=models.CASCADE, related_name='territoriales'
    )
    usuario = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):
        return f"Territorial de {self.usuario}"


class Derivacion(models.Model):
    fecha_derivacion = models.DateTimeField()
    fecha_finalizacion = models.DateTimeField(null=True, blank=True)
    incidencia = models.ForeignKey(Incidencia, on_delete=models.CASCADE)
    jefe_cuadrilla = models.ForeignKey(JefeCuadrilla, on_delete=models.CASCADE)

    def __str__(self):
        return f"Derivación de {self.incidencia}"
    
class PreguntaBase(models.Model):
    tipo_incidencia = models.ForeignKey(TipoIncidencia, on_delete=models.CASCADE, related_name='preguntas_base')
    texto_pregunta = models.CharField(max_length=200)
    tipo = models.CharField(max_length=50, choices=[
            ('texto', 'Texto'),
            ('numero', 'Número'),
            ('opcion', 'Opción múltiple')
        ],
        default='texto'
    )

    def __str__(self):
        return f"{self.tipo_incidencia.nombre_problema} - {self.texto_pregunta}"

