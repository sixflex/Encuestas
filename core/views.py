
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q

from .forms import UsuarioCrearForm, UsuarioEditarForm
from .utils import solo_admin 

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
    return render(request, "core/usuarios_lista.html", {"usuarios": qs, "q": q})

@login_required
@solo_admin
@transaction.atomic
def usuario_crear(request):
    if request.method == "POST":
        form = UsuarioCrearForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Usuario '{user.username}' creado.")
            return redirect("core:usuarios_lista")
    else:
        form = UsuarioCrearForm(initial={"is_active": True, "is_staff": False})
    return render(request, "core/usuario_form.html", {"form": form, "modo": "crear"})

@login_required
@solo_admin
@transaction.atomic
def usuario_editar(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        form = UsuarioEditarForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Usuario '{user.username}' actualizado.")
            return redirect("core:usuarios_lista")
    else:
        form = UsuarioEditarForm(instance=user)
    return render(request, "core/usuario_form.html", {"form": form, "modo": "editar", "obj": user})

@login_required
@solo_admin
@transaction.atomic
def usuario_toggle_activo(request, pk):
    """
    Activa/Desactiva al usuario en vez de eliminarlo.
    - Si está activo -> lo desactiva (bloquea inicio de sesión).
    - Si está inactivo -> lo activa.
    """
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        user.is_active = not user.is_active
        user.save(update_fields=["is_active"])
        estado = "activado" if user.is_active else "desactivado"
        messages.success(request, f"Usuario '{user.username}' {estado}.")
        return redirect("core:usuarios_lista")

    # Confirmación simple (opcional). Puedes redirigir directo si no quieres confirmación.
    return render(request, "core/usuario_toggle_confirm.html", {"obj": user})

@login_required
@solo_admin
def usuario_detalle(request, pk):
    user = get_object_or_404(User, pk=pk)
    groups = list(user.groups.values_list("name", flat=True))
    return render(request, "core/usuario_detalle.html", {"obj": user, "groups": groups})
