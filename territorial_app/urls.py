from django.urls import path
from . import views

app_name = "territorial_app"

urlpatterns = [
    path("territorial/incidencias/", views.lista_incidencias, name="incidencias_lista"),
    path("territorial/<int:pk>/incidencia_validar/", views.validar_incidencia, name="incidencia_validar"),
    path("territorial/<int:pk>/incidencia_rechazar/", views.rechazar_incidencia, name="incidencia_rechazar"),
    path("territorial/<int:pk>/incidencia_reasignar/", views.reasignar_incidencia, name="incidencia_reasignar"),
]
