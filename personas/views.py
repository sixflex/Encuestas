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

@login_required
def dashboard_admin(request):
    return render(request, "personas/dashboards/admin.html")

@login_required
def dashboard_territorial(request):
    return render(request, "personas/dashboards/territorial.html")

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
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        return redirect("login")

    rol = profile.group.name
    if rol == "Administrador":
        return redirect("personas:dashboard_admin")
    elif rol == "Territorial":
        return redirect("personas:dashboard_territorial")
    elif rol == "Jefe de Cuadrilla":
        return redirect("personas:dashboard_jefeCuadrilla")
    elif rol == "Dirección":
        return redirect("personas:dashboard_direccion")
    elif rol == "Departamento":
        return redirect("personas:dashboard_departamento")
    else:
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
            return redirect("usuarios_lista")
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
            return redirect("usuarios_lista")
    else:
        form = UsuarioEditarForm(instance=user)
    return render(request, "personas/usuario_form.html", {"form": form, "modo": "editar", "obj": user})

# 🔁 NUEVO: activar/desactivar (sin eliminar)
@login_required
@solo_admin
@require_POST
def usuario_toggle_activo(request, pk):
    user = get_object_or_404(User, pk=pk)

    # Evitar que un admin se auto-desactive (opcional pero recomendado)
    if user == request.user and user.is_active:
        messages.warning(request, "No puedes desactivar tu propio usuario mientras estás conectado.")
        return redirect("usuarios_lista")

    user.is_active = not user.is_active
    user.save(update_fields=["is_active"])

    estado = "activado" if user.is_active else "desactivado"
    messages.success(request, f"Usuario '{user.username}' {estado}.")
    return redirect("usuarios_lista")

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
    return redirect("/accounts/login")
