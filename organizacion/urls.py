from django.urls import path, include
from . import views

app_name = "organizacion"  # si usas namespacing en include()

urlpatterns = [
    path("direccion/", views.direcciones_lista, name="direcciones_lista"),
    path("direccion/nuevo/", views.direccion_crear, name="direccion_crear"),
    path("direccion/<int:pk>/", views.direccion_editar, name="direccion_editar"),
    path("direccion/<int:pk>/detalle/", views.direccion_detalle, name="direccion_detalle"),
    path("direccion/<int:pk>/eliminar/", views.direccion_eliminar, name="direccion_eliminar"),

    path("departamento/", views.departamentos_lista, name="departamentos_lista"),
    path("departamento/nuevo/", views.departamento_crear, name="departamento_crear"),
    path("departamento/<int:pk>/", views.departamento_editar, name="departamento_editar"),
    path("departamento/<int:pk>/detalle/", views.departamento_detalle, name="departamento_detalle"),
    path("departamento/<int:pk>/eliminar/", views.departamento_eliminar, name="departamento_eliminar"),
    
    # Asignación de cuadrillas
    path("asignar-cuadrilla/<int:pk>/", views.asignar_cuadrilla_view, name="asignar_cuadrilla"),
]
