from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth import logout
from registration.models import Profile
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.views.decorators.http import require_POST
from .forms import UsuarioCrearForm, UsuarioEditarForm
from .utils import solo_admin
from core.models import Incidencia

@login_required
def dashboard_admin(request):
    return render(request, "personas/dashboards/admin.html")

@login_required
def dashboard_territorial(request):
    # Obtener las últimas 10 incidencias para mostrar en el dashboard
    incidencias = Incidencia.objects.all().order_by('-creadoEl')[:10]
    return render(request, "personas/dashboards/territorial.html", {
        'incidencias': incidencias
    })

@login_required
def dashboard_jefe(request):
    return render(request, "personas/dashboards/jefeCuadrilla.html")

@login_required
def dashboard_direccion(request):
    return render(request, "personas/dashboards/direccion.html")

@login_required
def dashboard_departamento(request):
    return render(request, "personas/dashboards/departamento.html")


@login_required
def check_profile(request):
    """
    Redirige al usuario al dashboard correspondiente según su rol.
    """
    user = request.user
    
    # Si es superusuario, va directo al admin
    if user.is_superuser:
        return redirect("personas:dashboard_admin")
    
    grupos = list(user.groups.values_list("name", flat=True))

    try:
        profile = Profile.objects.select_related('group').get(user=user)
    except Profile.DoesNotExist:
        messages.error(request, "No se encontró un perfil asociado a este usuario.")
        logout(request)
        return redirect("login")

    # Obtener el nombre del grupo y limpiarlo
    if not profile.group:
        messages.error(request, "Tu usuario no tiene un grupo/rol asignado. Contacta al administrador.")
        logout(request)
        return redirect("login")
    
    rol = profile.group.name.strip()
    
    # Debug: puedes comentar esto después de probar
    print(f"Usuario: {user.username}, Rol: '{rol}'")
    
    # Redirección según el rol
    if "Administrador" in grupos:
        return redirect("personas:dashboard_admin")
    elif "Territorial" in grupos:
        return redirect("personas:dashboard_territorial")
    elif "Jefe de Cuadrilla" in grupos:
        return redirect("personas:dashboard_jefeCuadrilla")
    elif "Dirección"in grupos:
        return redirect("personas:dashboard_direccion")
    elif "Departamento"in grupos:
        return redirect("personas:dashboard_departamento")
    else:
        messages.error(request, f"Rol '{rol}' no reconocido. Contacta al administrador.")
        logout(request)
        return redirect("login")
    

@login_required
@solo_admin
def usuarios_lista(request):
    q = request.GET.get("q", "").strip()
    qs = User.objects.all().order_by("id")
    if q:
        qs = qs.filter(
            Q(username__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(email__icontains=q)
        )
    return render(request, "personas/usuarios_lista.html", {"usuarios": qs, "q": q})

@login_required
@solo_admin
def usuario_crear(request):
    if request.method == "POST":
        form = UsuarioCrearForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Usuario '{user.username}' creado.")
            return redirect("personas:usuarios_lista")
    else:
        form = UsuarioCrearForm(initial={"is_active": True, "is_staff": False})
    return render(request, "personas/usuario_form.html", {"form": form, "modo": "crear"})

@login_required
@solo_admin
def usuario_editar(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        form = UsuarioEditarForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Usuario '{user.username}' actualizado.")
            return redirect("personas:usuarios_lista")
    else:
        form = UsuarioEditarForm(instance=user)
    return render(request, "personas/usuario_form.html", {"form": form, "modo": "editar", "obj": user})

@login_required
@solo_admin
@require_POST
def usuario_toggle_activo(request, pk):
    user = get_object_or_404(User, pk=pk)

    if user == request.user and user.is_active:
        messages.warning(request, "No puedes desactivar tu propio usuario mientras estás conectado.")
        return redirect("personas:usuarios_lista")

    user.is_active = not user.is_active
    user.save(update_fields=["is_active"])

    estado = "activado" if user.is_active else "desactivado"
    messages.success(request, f"Usuario '{user.username}' {estado}.")
    return redirect("personas:usuarios_lista")

@login_required
@solo_admin
def usuario_detalle(request, pk):
    user = get_object_or_404(User, pk=pk)
    groups = list(user.groups.values_list("name", flat=True))
    return render(request, "personas/usuario_detalle.html", {"obj": user, "groups": groups})

def cerrar_sesion(request):
    logout(request)
    request.session.flush()
    messages.info(request, "Sesión cerrada correctamente.")
    return redirect("/accounts/login/")