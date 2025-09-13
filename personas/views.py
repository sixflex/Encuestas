from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
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

@login_required
@solo_admin
def usuario_eliminar(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        uname = user.username
        user.delete()
        messages.success(request, f"Usuario '{uname}' eliminado.")
        return redirect("usuarios_lista")
    return render(request, "personas/usuario_confirm_delete.html", {"obj": user})

@login_required
@solo_admin
def usuario_detalle(request, pk):
    user = get_object_or_404(User, pk=pk)
    groups = list(user.groups.values_list("name", flat=True))
    return render(request, "personas/usuario_detalle.html", {"obj": user, "groups": groups})
