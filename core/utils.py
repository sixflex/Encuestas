from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps # Necesario para decoradores personalizados

def es_admin(u):
    # Admin por grupo o superusuario Django
    return u.is_authenticated and (u.is_superuser or u.groups.filter(name="Administrador").exists())

#cambios barbara
def es_territorial(u):
    # Verifica si el usuario es Territorial
    return u.is_authenticated and u.groups.filter(name="Territorial").exists()

def es_admin_o_territorial(u):
    # Admin o Territorial pueden acceder
    return u.is_authenticated and (
        u.is_superuser or 
        u.groups.filter(name__in=["Administrador", "Territorial"]).exists()
    )


#----------------------------------

def solo_admin(function):
    """
    Decorador que solo permite el acceso a Administradores.
    Si falla, redirige a 'home' (el dashboard principal) con un mensaje de error.
    """
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if es_admin(request.user):
            # Si pasa la prueba, ejecuta la vista
            return function(request, *args, **kwargs)
        
        # Si no pasa la prueba:
        messages.error(request, "No tienes permisos de Administrador para acceder a esta página.")
        return redirect('home') # 'home' es la URL que redirige al check_profile
    return wrap


def solo_territorial(function):
    """
    Decorador que solo permite el acceso a Territorial (y Admin, si se desea).
    Si falla, redirige a 'home' con un mensaje de error.
    """
    @wraps(function)
    def wrap(request, *args, **kwargs):
        # Ajuste: Generalmente, un Admin puede hacer lo que hace un Territorial
        if es_admin(request.user) or es_territorial(request.user):
            return function(request, *args, **kwargs)
        
        messages.error(request, "No tienes permisos de Territorial para acceder a esta página.")
        return redirect('home')
    return wrap


def admin_o_territorial(function):
    """
    Decorador que solo permite el acceso a Admin o Territorial.
    Si falla, redirige a 'home' con un mensaje de error.
    """
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if es_admin_o_territorial(request.user):
            return function(request, *args, **kwargs)
        messages.error(request, "No tienes permisos para acceder a esta página.")
        return redirect('home')
    return wrap

# mas decoradores
def solo_direccion(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        grupos = set(request.user.groups.values_list("name", flat=True))
        if "Dirección" in grupos or request.user.is_superuser:
            return function(request, *args, **kwargs)
        
        messages.error(request, "No tienes permisos para acceder a este dashboard.")
        return redirect('home')
    return wrap

def solo_cuadrilla(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        grupos = set(request.user.groups.values_list("name", flat=True))
        if "Jefe de Cuadrilla" in grupos or request.user.is_superuser:
            return function(request, *args, **kwargs)
        
        messages.error(request, "No tienes permisos para acceder a este dashboard.")
        return redirect('home')
    return wrap

def admin_territorial_cuadrilla(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        grupos = request.user.groups.values_list("name", flat=True)
        if set(grupos) & {"Administrador", "Territorial", "Jefe de Cuadrilla"}:
            return view_func(request, *args, **kwargs)
        messages.error(request, "No tienes permisos para acceder a este dashboard.")
        return redirect('home')
    return wrapper
