from django.urls import path, include
from . import views
from incidencias import views as incidencias_views

app_name = "territorial_app"
urlpatterns = [
    #path("territorial/incidencias/", views.lista_incidencias, name="incidencias_lista"),
    path("territorial/<int:pk>/validar_incidencia/", views.validar_incidencia, name="validar_incidencia"),
    path("territorial/<int:pk>/rechazar_incidencia/", views.rechazar_incidencia, name="rechazar_incidencia"),
    path("territorial/<int:pk>/reasignar_incidencia/", views.reasignar_incidencia, name="reasignar_incidencia"),
    path("incidencias/", incidencias_views.incidencias_lista, name="incidencias_lista"),
    path("incidencias/editar", incidencias_views.incidencia_editar, name="incidencia_editar"),

]
