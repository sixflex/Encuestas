from django.db import models
from registration.models import Profile


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
    direccion = models.ForeignKey('core.Direccion', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.nombre_departamento


class TipoIncidencia(models.Model):
    nombre_problema = models.CharField(max_length=100)
    descripcion = models.TextField()
    tipo_gravedad = models.CharField(
        max_length=1,
        choices=[('A', 'Alta'), ('M', 'Media'), ('B', 'Baja')]
    )

    def __str__(self):
        return self.nombre_problema


class Encuesta(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    ubicacion = models.CharField(max_length=200)
    estado = models.BooleanField(default=True)
    creadoEl = models.DateTimeField(auto_now_add=True)
    actualizadoEl = models.DateTimeField(auto_now=True)
    prioridad = models.CharField(max_length=50)
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE)

    tipo_incidencia = models.ForeignKey(
        'TipoIncidencia', on_delete=models.SET_NULL, null=True, blank=True, related_name='encuestas'
    )

    def __str__(self):
        return self.titulo


class PreguntaEncuesta(models.Model):
    texto_pregunta = models.CharField(max_length=200)
    descripcion = models.TextField()
    tipo = models.CharField(max_length=50)
    encuesta = models.ForeignKey('core.Encuesta', on_delete=models.CASCADE)

    def __str__(self):
        return self.texto_pregunta


class RespuestaEncuesta(models.Model):
    texto_respuesta = models.TextField()
    tipo = models.CharField(max_length=50)
    pregunta = models.ForeignKey('core.PreguntaEncuesta', on_delete=models.CASCADE)

    def __str__(self):
        return self.texto_respuesta[:50]


class JefeCuadrilla(models.Model):
    nombre_cuadrilla = models.CharField(max_length=100)
    encargado = models.ForeignKey(
        Profile, on_delete=models.SET_NULL, null=True, related_name='cuadrillas_encargadas'
    )
    departamento = models.ForeignKey('core.Departamento', on_delete=models.SET_NULL, null=True)
    usuario = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='cuadrillas'
    )

    def __str__(self):
        return self.nombre_cuadrilla


class Incidencia(models.Model):
    ESTADO_CHOICES = (
        ('Pendiente', 'Pendiente'),
        ('En Progreso', 'En Progreso'),
        ('Completada', 'Completada'),
        ('Rechazada', 'Rechazada'),
        ('Validada', "Validada"),
    )

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    estado = models.CharField(max_length=50, choices=ESTADO_CHOICES, default='Pendiente')
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

    cuadrilla = models.ForeignKey('core.JefeCuadrilla', on_delete=models.SET_NULL, null=True)
    respuesta = models.ForeignKey('core.RespuestaEncuesta', on_delete=models.SET_NULL, null=True)
    departamento = models.ForeignKey('core.Departamento', on_delete=models.SET_NULL, null=True)
    encuesta = models.ForeignKey('core.Encuesta', on_delete=models.SET_NULL, null=True)
    tipo_incidencia = models.ForeignKey('core.TipoIncidencia', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.titulo


class Multimedia(models.Model):
    nombre = models.CharField(max_length=100)
    url = models.URLField()
    tipo = models.CharField(max_length=50)
    formato = models.CharField(max_length=50)
    creadoEl = models.DateTimeField(auto_now_add=True)
    incidencia = models.ForeignKey('core.Incidencia', on_delete=models.CASCADE, related_name="multimedias")

    def __str__(self):
        return self.nombre


class Territorial(models.Model):
    incidencia = models.ForeignKey('core.Incidencia', on_delete=models.CASCADE, related_name='territoriales')
    usuario = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):
        return f"Territorial de {self.usuario}"


class Derivacion(models.Model):
    fecha_derivacion = models.DateTimeField()
    fecha_finalizacion = models.DateTimeField(null=True, blank=True)
    incidencia = models.ForeignKey('core.Incidencia', on_delete=models.CASCADE)
    jefe_cuadrilla = models.ForeignKey('core.JefeCuadrilla', on_delete=models.CASCADE)

    def __str__(self):
        return f"Derivación de {self.incidencia}"


class PreguntaDefaultTipo(models.Model):
    TIPO_CHOICES = (
        ('texto', 'Texto'),
        ('numero', 'Número'),
        ('opcion', 'Opción'),
        ('fecha', 'Fecha'),
    )

    tipo_incidencia = models.ForeignKey(
        'core.TipoIncidencia',
        on_delete=models.CASCADE,
        related_name='preguntas_default'
    )
    texto_pregunta = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES, default='texto')
    orden = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['orden', 'id']

    def __str__(self):
        return f"[{self.tipo_incidencia}] {self.texto_pregunta}"
