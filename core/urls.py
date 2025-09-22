from django.urls import path
from .views import (
    usuarios_lista, usuario_crear, usuario_editar,
    usuario_eliminar, usuario_detalle
)

urlpatterns = [
    path("usuarios/", usuarios_lista, name="usuarios_lista"),
    path("usuarios/nuevo/", usuario_crear, name="usuario_crear"),
    path("usuarios/<int:pk>/", usuario_detalle, name="usuario_detalle"),
    path("usuarios/<int:pk>/editar/", usuario_editar, name="usuario_editar"),
    path("usuarios/<int:pk>/eliminar/", usuario_eliminar, name="usuario_eliminar"),
]
