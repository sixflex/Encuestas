from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q #cambio barbara
from core.models import Incidencia, JefeCuadrilla, Departamento, Encuesta
from .forms import RechazarIncidenciaForm, ReasignarIncidenciaForm, EncuestaForm, FinalizarIncidenciaForm #cambio barbara
from core.utils import solo_admin, admin_o_territorial

from django.db import transaction
from django.forms import formset_factory
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from core.models import Encuesta, PreguntaEncuesta, TipoIncidencia, PreguntaDefaultTipo
from .forms import EncuestaConTipoForm, PreguntaFormSet, PreguntaSimpleForm
from core.utils import admin_o_territorial
# ---------------------------------
# Lista de incidencias
# ---------------------------------


@login_required
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


# Reasignar incidencia
@login_required
def reasignar_incidencia(request, pk):
    incidencia = get_object_or_404(Incidencia, pk=pk)
    user = request.user
    grupos = list(user.groups.values_list("name", flat=True))
    is_admin = "Administrador" in grupos or user.is_superuser
    is_territorial = "Territorial" in grupos
    is_departamento = "Departamento" in grupos

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
    ctx = {
        'form': form,
        'incidencia': incidencia,
        'is_admin': is_admin,
        'is_territorial': is_territorial,
        'is_departamento': is_departamento,
    }

    return render(request,'territorial_app/reasignar_incidencia.html', ctx)

'''
#cambios barbara, esta malo asi que deje el del bernardo, ese funciona
@login_required
def reasignar_incidencia(request, pk):
    incidencia = get_object_or_404(Incidencia, pk=pk)

    if request.method == 'POST':
        form = ReasignarIncidenciaForm(request.POST, instance=incidencia)
        if form.is_valid():
            incidencia_obj = form.save(commit=False)
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
'''
# Finalizar incidencia

@login_required
def finalizar_incidencia(request, pk):
    incidencia = get_object_or_404(Incidencia, pk=pk)

    try:
        jefe_cuadrilla = JefeCuadrilla.objects.get(usuario__user=request.user)
    except JefeCuadrilla.DoesNotExist:
        messages.error(request, "No tienes permisos para finalizar incidencias.")
        return redirect('territorial_app:incidencias_lista')

    if incidencia.cuadrilla != jefe_cuadrilla:
        messages.error(request, "No puedes finalizar una incidencia que no pertenece a tu cuadrilla.")
        return redirect('territorial_app:incidencias_lista')

    if request.method == 'POST':
        form = FinalizarIncidenciaForm(request.POST, request.FILES, instance=incidencia)
        if form.is_valid():
            incidencia = form.save(commit=False)
            incidencia.estado = 'Finalizada'
            incidencia.fecha_finalizacion = timezone.now()
            incidencia.save()
            messages.success(request, f"La incidencia '{incidencia.titulo}' ha sido finalizada.")
            return redirect('territorial_app:incidencias_lista')
    else:
        form = FinalizarIncidenciaForm(instance=incidencia)

    return render(
        request,
        'territorial_app/finalizar_incidencia.html',
        {'form': form, 'incidencia': incidencia}
    )
    
@login_required
@admin_o_territorial
def encuestas_lista(request):
    """
    Lista todas las encuestas.
    Territorial y Admin pueden verlas todas.
    """
    q = request.GET.get("q", "").strip()
    estado = request.GET.get("estado")  # 'activo' | 'inactivo' | None
    
    qs = Encuesta.objects.all().select_related('departamento').order_by('-creadoEl')
    
    # Filtro por búsqueda de texto
    if q:
        qs = qs.filter(
            Q(titulo__icontains=q) | 
            Q(descripcion__icontains=q) |
            Q(departamento__nombre_departamento__icontains=q)
        )
    
    # Filtro por estado
    if estado == 'activo':
        qs = qs.filter(estado=True)
    elif estado == 'inactivo':
        qs = qs.filter(estado=False)
    
    ctx = {
        "encuestas": qs,
        "q": q,
        "estado_seleccionado": estado,
    }
    return render(request, "territorial_app/encuestas_lista.html", ctx)


@login_required
@admin_o_territorial
def encuesta_detalle(request, pk):
    """
    Muestra el detalle de una encuesta.
    """
    encuesta = get_object_or_404(Encuesta, pk=pk)
    return render(request, "territorial_app/encuesta_detalle.html", {"encuesta": encuesta})


@login_required
@admin_o_territorial
def encuesta_crear(request):
    if request.method == "POST":
        form = EncuestaForm(request.POST)
        if form.is_valid():
            encuesta = form.save()

            tipo = encuesta.tipo_incidencia
            if tipo:
                defaults = PreguntaDefaultTipo.objects.filter(tipo_incidencia=tipo)
                for p in defaults:
                    PreguntaEncuesta.objects.create(
                        texto_pregunta=p.texto_pregunta,
                        descripcion=p.descripcion,
                        tipo=p.tipo,
                        encuesta=encuesta
                    )

            messages.success(request, f"Encuesta '{encuesta.titulo}' creada con preguntas por defecto.")
            return redirect("territorial_app:encuestas_lista")
    else:
        form = EncuestaForm(initial={'estado': True, 'prioridad': 'Normal'})

    return render(request, "territorial_app/encuesta_form.html", {
        "form": form,
        "modo": "crear"
    })



@login_required
@admin_o_territorial
def encuesta_editar(request, pk):
    """
    Edita una encuesta existente.
    Según requerimientos: solo se puede editar si está bloqueada (inactiva).
    """
    encuesta = get_object_or_404(Encuesta, pk=pk)
    
    # Validación: no se puede editar una encuesta activa
    if encuesta.estado and request.method == "POST":
        messages.error(request, "No se puede editar una encuesta activa. Debes desactivarla primero.")
        return redirect("territorial_app:encuesta_detalle", pk=pk)
    
    if request.method == "POST":
        form = EncuestaForm(request.POST, instance=encuesta)
        if form.is_valid():
            encuesta = form.save()
            messages.success(request, f"Encuesta '{encuesta.titulo}' actualizada correctamente.")
            return redirect("territorial_app:encuestas_lista")
    else:
        form = EncuestaForm(instance=encuesta)
    
    return render(request, "territorial_app/encuesta_form.html", {
        "form": form,
        "modo": "editar",
        "encuesta": encuesta
    })


@login_required
@admin_o_territorial
def encuesta_toggle_estado(request, pk):
    """
    Activa o desactiva (bloquea) una encuesta.
    Según requerimientos: cambiar entre activa/bloqueada.
    """
    if request.method != "POST":
        messages.error(request, "Método no permitido.")
        return redirect("territorial_app:encuestas_lista")
    
    encuesta = get_object_or_404(Encuesta, pk=pk)
    encuesta.estado = not encuesta.estado
    encuesta.save(update_fields=['estado', 'actualizadoEl'])
    
    estado_texto = "activada" if encuesta.estado else "bloqueada"
    messages.success(request, f"Encuesta '{encuesta.titulo}' {estado_texto} correctamente.")
    
    return redirect("territorial_app:encuestas_lista")


@login_required
@admin_o_territorial
def encuesta_eliminar(request, pk):
    """
    Elimina una encuesta.
    Opcional: podrías requerir que esté bloqueada para eliminarla.
    """
    encuesta = get_object_or_404(Encuesta, pk=pk)
    
    # Opcional: solo permitir eliminar si está bloqueada
    if encuesta.estado:
        messages.error(request, "No se puede eliminar una encuesta activa. Debes desactivarla primero.")
        return redirect("territorial_app:encuesta_detalle", pk=pk)
    
    if request.method == "POST":
        titulo = encuesta.titulo
        encuesta.delete()
        messages.success(request, f"Encuesta '{titulo}' eliminada correctamente.")
        return redirect("territorial_app:encuestas_lista")
    
    return render(request, "territorial_app/encuesta_eliminar.html", {"encuesta": encuesta})


@login_required
@admin_o_territorial
@transaction.atomic
def encuesta_crear(request):
    # Construimos el formset vacío; lo rellenamos con initial en GET si viene ?tipo=
    if request.method == "POST":
        form = EncuestaConTipoForm(request.POST)
        formset = PreguntaFormSet(request.POST, prefix="p")
        if form.is_valid() and formset.is_valid():
            encuesta = form.save(commit=False)
            encuesta.tipo_incidencia = form.cleaned_data['tipo_incidencia']
            encuesta.save()

            # Crear preguntas
            for f in formset:
                if f.cleaned_data and not f.cleaned_data.get('DELETE', False):
                    PreguntaEncuesta.objects.create(
                        encuesta=encuesta,
                        texto_pregunta=f.cleaned_data['texto_pregunta'],
                        descripcion=f.cleaned_data.get('descripcion', ''),
                        tipo=f.cleaned_data['tipo'],
                    )
            messages.success(request, f"Encuesta '{encuesta.titulo}' creada con preguntas.")
            return redirect("territorial_app:encuestas_lista")
    else:
        initial = []
        tipo_id = request.GET.get('tipo')
        if tipo_id:
            try:
                t = TipoIncidencia.objects.get(pk=tipo_id)
                for pd in t.preguntas_default.all():
                    initial.append({
                        'texto_pregunta': pd.texto_pregunta,
                        'descripcion': pd.descripcion,
                        'tipo': pd.tipo,
                    })
            except TipoIncidencia.DoesNotExist:
                pass

        form = EncuestaConTipoForm(initial={'estado': True, 'prioridad': 'Normal'})
        formset = PreguntaFormSet(initial=initial, prefix="p")

    return render(request, "territorial_app/encuesta_form.html", {
        "form": form,
        "modo": "crear",
        "formset": formset
    })