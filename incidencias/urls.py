from django.urls import path
from . import views
from . import views_clasificacion

app_name = "incidencias"

urlpatterns = [
    # (Categorías eliminadas del modelo) -- rutas removidas para evitar import errors
    
    # API endpoints
    path("api/cuadrillas-por-departamento/<int:departamento_id>/", views.cuadrillas_por_departamento, name="cuadrillas_por_departamento"),

    # URLs de Tipos de Incidencia
    path("tipos/", views_clasificacion.tipo_lista, name="tipo_lista"),
    path("tipos/nuevo/", views_clasificacion.tipo_crear, name="tipo_crear"),
    path("tipos/<int:pk>/editar/", views_clasificacion.tipo_editar, name="tipo_editar"),
    # El toggle de tipo dependía de un campo 'estado' que ya no existe; ruta removida
    path("tipos/<int:pk>/eliminar/", views_clasificacion.tipo_eliminar, name="tipo_eliminar"),

    path("incidencias/", views.incidencias_lista, name ="incidencias_lista"),
    path("incidencias/nuevo/", views.incidencia_crear, name = "incidencia_crear"),
    path("incidencias/<int:pk>/", views.incidencia_editar, name = "incidencia_editar") ,
    path("incidencias/<int:pk>/detalle/", views.incidencia_detalle, name = "incidencia_detalle"), 
    path("incidencias/<int:pk>/eliminar/", views.incidencia_eliminar, name = "incidencia_eliminar"),
    path("incidencias/<int:pk>/subir-evidencia/", views.subir_evidencia, name = "subir_evidencia"),
    path("incidencias/<int:pk>/finalizar/", views.finalizar_incidencia, name = "finalizar_incidencia"),
]