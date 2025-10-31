from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
<<<<<<< HEAD
    # Panel de Administración
    path("dashboard/admin/", views.dashboard_admin, name="dashboard_admin"),
=======
>>>>>>> 57b9c8f85e4d82613d934e94c986dca7655e2f87
    path("usuarios/", views.usuarios_lista, name="usuarios_lista"),
    path("usuarios/nuevo/", views.usuario_crear, name="usuario_crear"),
    path("usuarios/<int:pk>/", views.usuario_detalle, name="usuario_detalle"),
    path("usuarios/<int:pk>/editar/", views.usuario_editar, name="usuario_editar"),
    path("usuarios/<int:pk>/toggle/", views.usuario_toggle_activo, name="usuario_toggle_activo"),
]
