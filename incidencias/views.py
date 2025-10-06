from core.models import Incidencia
from django.shortcuts import render, redirect, get_object_or_404
from .forms import IncidenciaForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.utils import solo_admin

#-----------------CRUD DE INCIDENCIASS------------
@login_required
@solo_admin
def incidencias_lista(request):
    q = request.GET.get("q", "").strip()
    qs = Incidencia.objects.all().order_by("-creadoEl")
    if q:
        qs = qs.filter(titulo__icontains=q)
    return render(request, "incidencias/incidencias_lista.html", {"incidencias": qs, "q": q})

@login_required
@solo_admin
def incidencia_crear(request):
    if request.method == "POST":
        form = IncidenciaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Incidencia creada correctamente.")
            return redirect("incidencias:incidencias_lista")
    else:
        form = IncidenciaForm()
    return render(request, "incidencias/incidencia_form.html", {"form": form})

@login_required
@solo_admin
def incidencia_editar(request, pk):
    incidencia = get_object_or_404(Incidencia, pk=pk)
    if request.method == "POST":
        form = IncidenciaForm(request.POST, instance=incidencia)
        if form.is_valid():
            form.save()
            messages.success(request, "Incidencia actualizada correctamente.")
            return redirect("incidencias:incidencias_lista")
    else:
        form = IncidenciaForm(instance=incidencia)
    return render(request, "incidencias/incidencia_form.html", {"form": form})

@login_required
@solo_admin
def incidencia_detalle(request, pk):
    incidencia = get_object_or_404(Incidencia, pk=pk)
    return render(request, "incidencias/incidencia_detalle.html", {"obj": incidencia})

@login_required
@solo_admin
def incidencia_eliminar(request, pk):
    obj = get_object_or_404(Incidencia, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Incidencia eliminada correctamente.")
        return redirect("incidencias:incidencias_lista")
    return render(request, "incidencias/incidencia_eliminar.html", {"obj": obj})
