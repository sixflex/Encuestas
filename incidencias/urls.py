from django.urls import path
from . import views, views_clasificacion

app_name = "incidencias"

urlpatterns = [

    # API endpoints
    path(
        "api/cuadrillas-por-departamento/<int:departamento_id>/",
        views.cuadrillas_por_departamento,
        name="cuadrillas_por_departamento"
    ),

    # ----------------- Tipos de Incidencia -----------------
    path("tipos/", views_clasificacion.tipo_lista, name="tipo_lista"),
    path("tipos/nuevo/", views_clasificacion.tipo_crear, name="tipo_crear"),
    path("tipos/<int:pk>/editar/", views_clasificacion.tipo_editar, name="tipo_editar"),
    path("tipos/<int:pk>/eliminar/", views_clasificacion.tipo_eliminar, name="tipo_eliminar"),

    # ----------------- Preguntas Base -----------------
    path("tipos/<int:tipo_id>/preguntas/", views_clasificacion.preguntas_base_lista, name="preguntas_base_lista"),
    path("tipos/<int:tipo_id>/preguntas/nueva/", views_clasificacion.pregunta_base_crear, name="pregunta_base_crear"),
    path("preguntas/<int:pk>/editar/", views_clasificacion.pregunta_base_editar, name="pregunta_base_editar"),
    path("preguntas/<int:pk>/eliminar/", views_clasificacion.pregunta_base_eliminar, name="pregunta_base_eliminar"),
    

    # ----------------- Incidencias -----------------
    path("incidencias/", views.incidencias_lista, name="incidencias_lista"),
    path("incidencias/nuevo/", views.incidencia_crear, name="incidencia_crear"),
    path("incidencias/<int:pk>/", views.incidencia_editar, name="incidencia_editar"),
    path("incidencias/<int:pk>/detalle/", views.incidencia_detalle, name="incidencia_detalle"),
    path("incidencias/<int:pk>/eliminar/", views.incidencia_eliminar, name="incidencia_eliminar"),
    path("incidencias/<int:pk>/subir-evidencia/", views.subir_evidencia, name="subir_evidencia"),
    path("incidencias/<int:pk>/finalizar/", views.finalizar_incidencia, name="finalizar_incidencia"),
]
