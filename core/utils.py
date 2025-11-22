from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from functools import wraps

def es_admin(u):
    """Verifica si el usuario es Administrador o Superusuario"""
    return u.is_authenticated and (u.is_superuser or u.groups.filter(name="Administrador").exists())

def es_territorial(u):
    """Verifica si el usuario es Territorial"""
    return u.is_authenticated and u.groups.filter(name="Territorial").exists()

def es_admin_o_territorial(u):
    """Verifica si el usuario es Admin o Territorial"""
    return u.is_authenticated and (
        u.is_superuser or 
        u.groups.filter(name__in=["Administrador", "Territorial"]).exists()
    )

def es_direccion(u):
    """Verifica si el usuario es Dirección"""
    return u.is_authenticated and (
        u.is_superuser or 
        u.groups.filter(name="Dirección").exists()
    )

def es_departamento(u):
    """Verifica si el usuario es Departamento"""
    return u.is_authenticated and (
        u.is_superuser or 
        u.groups.filter(name="Departamento").exists()
    )

def es_cuadrilla(u):
    """Verifica si el usuario es Jefe de Cuadrilla"""
    return u.is_authenticated and (
        u.is_superuser or 
        u.groups.filter(name="Jefe de Cuadrilla").exists()
    )


# ============================================
# DECORADORES PERSONALIZADOS
# ============================================

def solo_admin(function):
    """
    Decorador que solo permite el acceso a Administradores.
    Si el usuario no está autenticado, redirige al login.
    Si está autenticado pero no tiene permisos, muestra mensaje y redirige al home.
    """
    @wraps(function)
    def wrap(request, *args, **kwargs):
        # Verificar autenticación
        if not request.user.is_authenticated:
            messages.warning(request, "Debes iniciar sesión para acceder.")
            return redirect('/accounts/login/')
        
        # Verificar permisos de administrador
        if es_admin(request.user):
            return function(request, *args, **kwargs)
        
        # Usuario autenticado pero sin permisos
        messages.error(request, "No tienes acceso a este dashboard")
        return redirect('personas:check_profile')  # Redirige a su dashboard correspondiente
    
    return wrap


def solo_territorial(function):
    """
    Decorador que solo permite el acceso a Territorial (y Admin).
    """
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Debes iniciar sesión para acceder.")
            return redirect('/accounts/login/')
        
        if es_admin(request.user) or es_territorial(request.user):
            return function(request, *args, **kwargs)
        
        messages.error(request, "No tienes acceso a este dashboard")
        return redirect('personas:check_profile')
    
    return wrap


def admin_o_territorial(function):
    """
    Decorador que solo permite el acceso a Admin o Territorial.
    """
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Debes iniciar sesión para acceder.")
            return redirect('/accounts/login/')
        
        if es_admin_o_territorial(request.user):
            return function(request, *args, **kwargs)
        
        messages.error(request, "No tienes acceso a este dashboard")
        return redirect('personas:check_profile')
    
    return wrap


def solo_direccion(function):
    """
    Decorador para usuarios con rol Dirección.
    """
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Debes iniciar sesión para acceder.")
            return redirect('/accounts/login/')
        
        if es_direccion(request.user):
            return function(request, *args, **kwargs)
        
        messages.error(request, "No tienes acceso a este dashboard")
        return redirect('personas:check_profile')
    
    return wrap


def solo_departamento(function):
    """
    Decorador para usuarios con rol Departamento.
    """
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Debes iniciar sesión para acceder.")
            return redirect('/accounts/login/')
        
        if es_departamento(request.user):
            return function(request, *args, **kwargs)
        
        messages.error(request, "No tienes acceso a este dashboard")
        return redirect('personas:check_profile')
    
    return wrap


def solo_cuadrilla(function):
    """
    Decorador para usuarios con rol Jefe de Cuadrilla.
    """
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Debes iniciar sesión para acceder.")
            return redirect('/accounts/login/')
        
        if es_cuadrilla(request.user):
            return function(request, *args, **kwargs)
        
        messages.error(request, "No tienes acceso a este dashboard")
        return redirect('personas:check_profile')
    
    return wrap


def admin_territorial_cuadrilla(function):
    """
    Decorador que permite acceso a Administrador, Territorial o Jefe de Cuadrilla.
    """
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Debes iniciar sesión para acceder.")
            return redirect('/accounts/login/')
        
        grupos = set(request.user.groups.values_list("name", flat=True))
        
        if request.user.is_superuser or grupos & {"Administrador", "Territorial", "Jefe de Cuadrilla"}:
            return function(request, *args, **kwargs)
        
        messages.error(request, "No tienes acceso a este dashboard")
        return redirect('personas:check_profile')
    
    return wrap
