from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.utils import solo_admin
from core.models import TipoIncidencia, PreguntaBase
from .forms_clasificacion import TipoIncidenciaForm, PreguntaBaseForm

# ----------------- CRUD Tipos de Incidencia -----------------
@login_required
@solo_admin
def tipo_lista(request):
    tipos = TipoIncidencia.objects.all()
    return render(request, 'tipo/tipo_lista.html', {'tipos': tipos})

@login_required
@solo_admin
def tipo_crear(request):
    if request.method == "POST":
        form = TipoIncidenciaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Tipo de incidencia creado correctamente.")
            return redirect('incidencias:tipo_lista')
    else:
        form = TipoIncidenciaForm()
    return render(request, 'tipo/tipo_form.html', {'form': form})

@login_required
@solo_admin
def tipo_editar(request, pk):
    tipo = get_object_or_404(TipoIncidencia, pk=pk)
    if request.method == "POST":
        form = TipoIncidenciaForm(request.POST, instance=tipo)
        if form.is_valid():
            form.save()
            messages.success(request, "Tipo de incidencia actualizado correctamente.")
            return redirect('incidencias:tipo_lista')
    else:
        form = TipoIncidenciaForm(instance=tipo)
    return render(request, 'tipo/tipo_form.html', {'form': form})

@login_required
@solo_admin
def tipo_eliminar(request, pk):
    tipo = get_object_or_404(TipoIncidencia, pk=pk)
    if request.method == "POST":
        tipo.delete()
        messages.success(request, "Tipo de incidencia eliminado correctamente.")
        return redirect('incidencias:tipo_lista')
    return render(request, 'tipo/tipo_eliminar.html', {'obj': tipo})

# ----------------- CRUD Preguntas Base -----------------
@login_required
@solo_admin
def preguntas_base_lista(request, tipo_id):
    tipo = get_object_or_404(TipoIncidencia, id=tipo_id)
    preguntas = tipo.preguntas_base.all()
    return render(request, 'tipo/preguntas_base_lista.html', {
        'tipo': tipo,
        'preguntas': preguntas
    })

@login_required
@solo_admin
def pregunta_base_crear(request, tipo_id):
    tipo = get_object_or_404(TipoIncidencia, id=tipo_id)
    if request.method == 'POST':
        form = PreguntaBaseForm(request.POST)
        if form.is_valid():
            pregunta = form.save(commit=False)
            pregunta.tipo_incidencia = tipo
            pregunta.save()
            messages.success(request, "Pregunta base creada correctamente.")
            return redirect('incidencias:preguntas_base_lista', tipo_id=tipo.id)
    else:
        form = PreguntaBaseForm()
    return render(request, 'tipo/pregunta_base_form.html', {'form': form, 'tipo': tipo})

@login_required
@solo_admin
def pregunta_base_editar(request, pk):
    pregunta = get_object_or_404(PreguntaBase, pk=pk)
    if request.method == 'POST':
        form = PreguntaBaseForm(request.POST, instance=pregunta)
        if form.is_valid():
            form.save()
            messages.success(request, "Pregunta base actualizada correctamente.")
            return redirect('incidencias:preguntas_base_lista', tipo_id=pregunta.tipo_incidencia.id)
    else:
        form = PreguntaBaseForm(instance=pregunta)
    return render(request, 'tipo/pregunta_base_form.html', {'form': form, 'tipo': pregunta.tipo_incidencia})

@login_required
@solo_admin
def pregunta_base_eliminar(request, pk):
    pregunta = get_object_or_404(PreguntaBase, pk=pk)
    tipo_id = pregunta.tipo_incidencia.id
    if request.method == 'POST':
        pregunta.delete()
        messages.success(request, "Pregunta base eliminada correctamente.")
        return redirect('incidencias:preguntas_base_lista', tipo_id=tipo_id)
    return render(request, 'tipo/pregunta_base_eliminar.html', {'pregunta': pregunta})
