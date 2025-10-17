from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.utils import solo_admin
from core.models import Direccion, Departamento
from .forms import DireccionForm, DepartamentoForm

# ------------------- CRUD DIRECCIONES -------------------
@login_required
@solo_admin
def direcciones_lista(request):
    q = request.GET.get("q", "").strip()
    qs = Direccion.objects.all().order_by("nombre_direccion")
    if q:
        qs = qs.filter(nombre_direccion__icontains=q)
    return render(request, "organizacion/direcciones_lista.html", {"direcciones": qs, "q": q})

@login_required
@solo_admin
def direccion_crear(request):
    if request.method == "POST":
        form = DireccionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("organizacion:direcciones_lista")
    else:
        form = DireccionForm()
    return render(request, "organizacion/direccion_form.html", {"form": form})

@login_required
@solo_admin
def direccion_editar(request, pk):
    direccion = get_object_or_404(Direccion, pk=pk)
    if request.method == "POST":
        form = DireccionForm(request.POST, instance=direccion)
        if form.is_valid():
            form.save()
            return redirect("organizacion:direcciones_lista")
    else:
        form = DireccionForm(instance=direccion)
    return render(request, "organizacion/direccion_form.html", {"form": form})

@login_required
@solo_admin
def direccion_detalle(request, pk):
    direccion = get_object_or_404(Direccion, pk=pk)
    grupo = None
    if direccion.encargado and direccion.encargado.group:
        grupo = direccion.encargado.group.name
    return render(request, "organizacion/direccion_detalle.html", {"obj": direccion,"grupo": grupo,})

@login_required
@solo_admin
def direccion_eliminar(request, pk):
    obj = get_object_or_404(Direccion, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Dirección eliminada correctamente.")
        return redirect("organizacion:direcciones_lista")
    return render(request, "organizacion/direccion_eliminar.html", {"obj": obj})

# ------------------- CRUD DEPARTAMENTOS -------------------

@login_required
@solo_admin
def departamentos_lista(request):
    q = request.GET.get("q", "").strip()
    qs = Departamento.objects.all().order_by("nombre_departamento")
    if q:
        qs = qs.filter(nombre_departamento__icontains=q)
    return render(request, "organizacion/departamentos_lista.html", {"departamentos": qs, "q": q})

@login_required
@solo_admin
def departamento_crear(request):
    if request.method == "POST":
        form = DepartamentoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("organizacion:departamentos_lista")
    else:
        form = DepartamentoForm()
    return render(request, "organizacion/departamento_form.html", {"form": form})

@login_required
@solo_admin
def departamento_editar(request, pk):
    departamento = get_object_or_404(Departamento, pk=pk)
    if request.method == "POST":
        form = DepartamentoForm(request.POST, instance=departamento)
        if form.is_valid():
            form.save()
            return redirect("organizacion:departamentos_lista")
    else:
        form = DepartamentoForm(instance=departamento)
    return render(request, "organizacion/departamento_form.html", {"form": form})

@login_required
@solo_admin
def departamento_detalle(request, pk):
    departamento = get_object_or_404(Departamento, pk=pk)
    grupo = None
    if departamento.encargado and departamento.encargado.group:
        grupo = departamento.encargado.group.name
    return render(request, "organizacion/departamento_detalle.html", {"obj": departamento, "grupo": grupo})

@login_required
@solo_admin
def departamento_eliminar(request, pk):
    obj = get_object_or_404(Departamento, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Departamento eliminado correctamente.")
        return redirect("organizacion:departamentos_lista")
    return render(request, "organizacion/departamento_eliminar.html", {"obj": obj})


@login_required
@solo_admin
def departamento_toggle_estado(request, pk):
    departamento = get_object_or_404(Departamento, pk=pk)
    if request.method == "POST":
        departamento.estado = not departamento.estado  # Cambia True <-> False
        departamento.save()
        if departamento.estado:
            messages.success(request, f"Departamento '{departamento.nombre_departamento}' desbloqueado.")
        else:
            messages.success(request, f"Departamento '{departamento.nombre_departamento}' bloqueado.")
    return redirect("organizacion:departamentos_lista")
