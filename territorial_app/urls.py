<<<<<<< HEAD
from django.urls import path
=======
from django.urls import path, include
>>>>>>> 57b9c8f85e4d82613d934e94c986dca7655e2f87
from . import views
from incidencias import views as incidencias_views

app_name = "territorial_app"
<<<<<<< HEAD

urlpatterns = [
    # ============================================
    # RUTAS DE INCIDENCIAS
    # ============================================
    path("territorial/<int:pk>/validar_incidencia/", views.validar_incidencia, name="validar_incidencia"),
    path("territorial/<int:pk>/rechazar_incidencia/", views.rechazar_incidencia, name="rechazar_incidencia"),
    path("territorial/<int:pk>/reasignar_incidencia/", views.reasignar_incidencia, name="reasignar_incidencia"),
    path("incidencias/", incidencias_views.incidencias_lista, name="incidencias_lista"),
    path("incidencias/editar", incidencias_views.incidencia_editar, name="incidencia_editar"),

    # ============================================
    # RUTAS DE ENCUESTAS (CRUD)
    # ============================================
    # Listar encuestas
    path("encuestas/", views.encuestas_lista, name="encuestas_lista"),
    
    # Crear encuesta
    path("encuestas/nueva/", views.encuesta_crear, name="encuesta_crear"),
    
    # Ver detalle de encuesta
    path("encuestas/<int:pk>/", views.encuesta_detalle, name="encuesta_detalle"),
    
    # Editar encuesta
    path("encuestas/<int:pk>/editar/", views.encuesta_editar, name="encuesta_editar"),
    
    # Activar/Bloquear encuesta (toggle estado)
    path("encuestas/<int:pk>/toggle/", views.encuesta_toggle_estado, name="encuesta_toggle_estado"),
    
    # Eliminar encuesta
    path("encuestas/<int:pk>/eliminar/", views.encuesta_eliminar, name="encuesta_eliminar"),
]
=======
urlpatterns = [
    #path("territorial/incidencias/", views.lista_incidencias, name="incidencias_lista"),
    path("territorial/<int:pk>/validar_incidencia/", views.validar_incidencia, name="validar_incidencia"),
    path("territorial/<int:pk>/rechazar_incidencia/", views.rechazar_incidencia, name="rechazar_incidencia"),
    path("territorial/<int:pk>/reasignar_incidencia/", views.reasignar_incidencia, name="reasignar_incidencia"),
    path("territorial/<int:pk>/finalizar_incidencia/", views.finalizar_incidencia, name="finalizar_incidencia"),

    path("incidencias/", incidencias_views.incidencias_lista, name="incidencias_lista"),
    path("incidencias/editar", incidencias_views.incidencia_editar, name="incidencia_editar"),
    

]
>>>>>>> 57b9c8f85e4d82613d934e94c986dca7655e2f87
