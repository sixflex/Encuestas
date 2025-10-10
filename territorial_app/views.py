<<<<<<< HEAD
from django.shortcuts import render

# Create your views here.
=======
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.models import Incidencia, JefeCuadrilla, Departamento
from .forms import RechazarIncidenciaForm, ReasignarIncidenciaForm
from core.utils import solo_admin

# ---------------------------------
# Lista de incidencias
# ---------------------------------
@login_required
@solo_admin
def lista_incidencias(request):
    user = request.user
    if user.groups.filter(name='Administrador').exists():
        incidencias = Incidencia.objects.all().order_by('-creadoEl')
    else:
        incidencias = Incidencia.objects.none()
    return render(
        request,
        'territorial_app/lista_incidencias.html',
        {'incidencias': incidencias}
    )

# ---------------------------------
# Validar incidencia
# ---------------------------------
@login_required
@solo_admin
def validar_incidencia(request, pk):
    incidencia = get_object_or_404(Incidencia, pk=pk)
    incidencia.estado = 'Validada'
    incidencia.fecha_cierre = timezone.now()
    incidencia.save()
    messages.success(request, f"Incidencia '{incidencia.titulo}' validada.")
    return redirect('territorial_app:incidencias_lista')

# ---------------------------------
# Rechazar incidencia
# ---------------------------------
@login_required
@solo_admin
def rechazar_incidencia(request, pk):
    incidencia = get_object_or_404(Incidencia, pk=pk)
    if request.method == 'POST':
        form = RechazarIncidenciaForm(request.POST)
        if form.is_valid():
            motivo = form.cleaned_data['motivo']
            incidencia.estado = 'Rechazada'
            incidencia.motivo_rechazo = motivo
            incidencia.fecha_cierre = timezone.now()
            incidencia.save()
            messages.success(request, f"Incidencia '{incidencia.titulo}' rechazada.")
            return redirect('territorial_app:incidencias_lista')
    else:
        form = RechazarIncidenciaForm()
    return render(
        request,
        'territorial_app/rechazar_incidencia.html',
        {'form': form, 'incidencia': incidencia}
    )

# ---------------------------------
# Reasignar incidencia
# ---------------------------------
@login_required
@solo_admin
def reasignar_incidencia(request, pk):
    incidencia = get_object_or_404(Incidencia, pk=pk)

    if request.method == 'POST':
        form = ReasignarIncidenciaForm(request.POST, instance=incidencia)
        if form.is_valid():
            incidencia_obj = form.save(commit=False)
            # directamente asignar la cuadrilla seleccionada
            incidencia_obj.cuadrilla = form.cleaned_data['cuadrilla']
            incidencia_obj.save()

            messages.success(
                request,
                f"Incidencia '{incidencia.titulo}' reasignada a departamento '{incidencia.departamento}'."
            )
            return redirect('territorial_app:incidencias_lista')
    else:
        form = ReasignarIncidenciaForm(instance=incidencia)

    return render(
        request,
        'territorial_app/reasignar_incidencia.html',
        {'form': form, 'incidencia': incidencia}
    )
>>>>>>> giuliana
