"""
URL configuration for encuestas project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
<<<<<<< HEAD
from django.conf import settings
from django.conf.urls.static import static
=======
>>>>>>> 57b9c8f85e4d82613d934e94c986dca7655e2f87

urlpatterns = [
    # Raíz: redirige al resolvedor de perfiles (decide dashboard por rol)
    path(
        "",
        RedirectView.as_view(pattern_name="personas:check_profile", permanent=False),
        name="home",
    ),

    # Autenticación (login/logout/reset…) usando los templates en templates/registration/
    path("accounts/", include("django.contrib.auth.urls")),

    # Apps del proyecto
    path("core/", include(("core.urls", "core"), namespace="core")),
    path("personas/", include(("personas.urls", "personas"), namespace="personas")),
    path("organizacion/", include(("organizacion.urls", "organizacion"), namespace="organizacion")),
<<<<<<< HEAD
    path("incidencias/", include(("incidencias.urls", "incidencias"), namespace="incidencias")),
=======
    path("incidencias/", include (("incidencias.urls", "incidencias"), namespace = "incidencias" )),
>>>>>>> 57b9c8f85e4d82613d934e94c986dca7655e2f87
    path("territorial/", include(("territorial_app.urls", "territorial_app"), namespace="territorial_app")),

    # Si tienes vistas extra en tu app registration (perfil, signup opcional, etc.)
    path("registration/", include(("registration.urls", "registration"), namespace="registration")),

    # Admin de Django
    path("admin/", admin.site.urls),
<<<<<<< HEAD
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
=======
]
>>>>>>> 57b9c8f85e4d82613d934e94c986dca7655e2f87
