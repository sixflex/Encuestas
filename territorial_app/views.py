from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from core.models import Incidencia, JefeCuadrilla, Departamento, Encuesta, PreguntaEncuesta, TipoIncidencia, PreguntaBase, RespuestaEncuesta, Multimedia
from .forms import RechazarIncidenciaForm, ReasignarIncidenciaForm, EncuestaForm, FinalizarIncidenciaForm, PreguntaEncuestaForm
from incidencias.forms import SubirEvidenciaForm
from core.utils import solo_admin, admin_o_territorial, admin_territorial_cuadrilla
from django.forms import formset_factory, modelformset_factory
from django.http import JsonResponse

#imports necesarios para evidencias
from django.http import JsonResponse
from .forms import EvidenciaForm
from core.models import Multimedia
import os

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

    encuesta = getattr(incidencia, 'encuesta', None)
    if encuesta:
        preguntas = encuesta.preguntaencuesta_set.all()
        incompletas = [p for p in preguntas if not p.respuestas.exists()]
        if incompletas:
            messages.error(
                request, 
                "No puedes completar la incidencia porque la encuesta asociada tiene preguntas sin responder."
            )
            return redirect('incidencias:incidencia_detalle', pk=incidencia.id)
    
    if request.method == 'POST':
        form = FinalizarIncidenciaForm(request.POST, request.FILES, instance=incidencia)
        if form.is_valid():
            incidencia = form.save(commit=False)
            incidencia.estado = 'Completada'
            incidencia.fecha_finalizacion = timezone.now()
            incidencia.save()
            messages.success(request, f"La incidencia '{incidencia.titulo}' ha sido Completada.")
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

    user = request.user
    is_admin = user.is_superuser or user.groups.filter(name="Administrador").exists()
    is_territorial = user.groups.filter(name="Territorial").exists()
    is_jefe = user.groups.filter(name="Jefe de Cuadrilla").exists()

    
    profile = request.user.profile 
    if is_jefe:
        profile = request.user.profile
        for encuesta in qs:
            encuesta.incidencia = encuesta.incidencia_set.filter(cuadrilla__usuario=profile).first()
    else:   
        for encuesta in qs:
            encuesta.incidencia = None

    
    ctx = {
        "encuestas": qs,
        "q": q,
        "estado_seleccionado": estado,
        "is_admin": is_admin,
        "is_territorial": is_territorial,
        "is_jefe": is_jefe,
    }
    return render(request, "territorial_app/encuestas_lista.html", ctx)


@login_required
#@admin_o_territorial
def encuesta_detalle(request, encuesta_id):
    """
    Muestra los detalles de una encuesta, sus preguntas y evidencias.
    """
    encuesta = get_object_or_404(Encuesta, pk=encuesta_id)
    preguntas = encuesta.preguntaencuesta_set.all().prefetch_related('respuestas')
    evidencias = encuesta.evidencias.all().order_by('-creadoEl')
    
    # Formulario para subir evidencias
    evidencia_form = EvidenciaForm()

    preguntas_con_respuestas = []
    for p in preguntas:
        respuesta = p.respuestas.first()
        texto = respuesta.texto_respuesta if respuesta and respuesta.texto_respuesta.strip() else "No respondida"
        preguntas_con_respuestas.append({
            "texto_pregunta": p.texto_pregunta,
            "tipo_pregunta": getattr(p, "tipo_pregunta", "texto"),
            "respuesta": texto
        })
    
    incidencia = encuesta.incidencia_set.first()

    return render(request, "territorial_app/encuesta_detalle.html", {
        "encuesta": encuesta,
        "preguntas_con_respuestas": preguntas_con_respuestas,
        "incidencia": incidencia,
        "evidencias": evidencias,
        "evidencia_form": evidencia_form,
    })




@login_required
@admin_o_territorial
def json_preguntas(request):
    tipo_id = request.GET.get('tipo')
    preguntas = []
    if tipo_id:
        preguntas = list(PreguntaBase.objects.filter(tipo_incidencia_id=tipo_id).values('texto_pregunta'))
    return JsonResponse(preguntas, safe=False)

@login_required
@admin_o_territorial
def encuesta_crear(request):
    PreguntaFormSet = formset_factory(PreguntaEncuestaForm, extra=0, can_delete=False)
    preguntas_base = []
    tipo_incidencia_id = None

    if request.method == 'POST':
        encuesta_form = EncuestaForm(request.POST)
        formset = PreguntaFormSet(request.POST, prefix='manual')

        tipo_incidencia_id = request.POST.get('tipo_incidencia')
        if tipo_incidencia_id:
            preguntas_base = PreguntaBase.objects.filter(tipo_incidencia_id=tipo_incidencia_id)

        # Botón agregar pregunta
        if 'agregar' in request.POST:
            # reconstruimos el formset conservando los datos del POST
            initial_list = []
            i = 0
            while f'manual-{i}-texto_pregunta' in request.POST:
                initial_list.append({'texto_pregunta': request.POST.get(f'manual-{i}-texto_pregunta')})
                i += 1
            # agregamos un formulario vacío
            initial_list.append({'texto_pregunta': ''})
            formset = PreguntaFormSet(initial=initial_list, prefix='manual')

        elif 'guardar' in request.POST:
            if encuesta_form.is_valid() and formset.is_valid():
                encuesta = encuesta_form.save()

                # Guardar preguntas base
                for pb in preguntas_base:
                    PreguntaEncuesta.objects.create(
                        encuesta=encuesta,
                        texto_pregunta=pb.texto_pregunta,
                        tipo=pb.tipo,
                        descripcion=''
                    )

                # Guardar preguntas manuales
                for f in formset.cleaned_data:
                    if f and f.get('texto_pregunta'):
                        PreguntaEncuesta.objects.create(
                            encuesta=encuesta,
                            texto_pregunta=f.get('texto_pregunta'),
                            tipo='texto',
                            descripcion=''
                        )

                return redirect('territorial_app:encuestas_lista')
    else:
        encuesta_form = EncuestaForm()
        formset = PreguntaFormSet(prefix='manual')

    return render(request, 'territorial_app/encuesta_form.html', {
        'encuesta_form': encuesta_form,
        'formset': formset,
        'preguntas_base': preguntas_base,
        'modo':'crear',
    })



@login_required
@admin_o_territorial
def pregunta_agregar(request, encuesta_id):
    from core.models import PreguntaEncuesta
    encuesta = get_object_or_404(Encuesta, pk=encuesta_id)

    if request.method == "POST":
        texto = request.POST.get("texto_pregunta")
        tipo = request.POST.get("tipo", "texto")
        descripcion = request.POST.get("descripcion", "")

        if texto:
            PreguntaEncuesta.objects.create(
                encuesta=encuesta,
                texto_pregunta=texto,
                descripcion=descripcion,
                tipo=tipo
            )
            messages.success(request, f"Pregunta agregada a la encuesta '{encuesta.titulo}'.")
            return redirect("territorial_app:encuesta_detalle", pk=encuesta.id)
        else:
            messages.error(request, "Debes escribir una pregunta antes de guardar.")

    return render(request, "territorial_app/pregunta_form.html", {"encuesta": encuesta})

@login_required
@admin_territorial_cuadrilla
def responder_encuesta(request, encuesta_id, incidencia_id):
    """
    Permite responder las preguntas de una encuesta.
    """
    encuesta = get_object_or_404(Encuesta, pk=encuesta_id)
    incidencia = get_object_or_404(Incidencia, pk=incidencia_id)
    preguntas = encuesta.preguntaencuesta_set.all().prefetch_related('respuestas')
    evidencia_form = SubirEvidenciaForm(request.POST or None, request.FILES or None)

    if request.method == "POST":
        for pregunta in preguntas:
            texto = request.POST.get(f"respuesta_{pregunta.id}", "").strip()
            if texto:
                # Guarda la respuesta: crea si no existe, actualiza si ya existe
                respuesta, created = RespuestaEncuesta.objects.get_or_create(
                    pregunta=pregunta,
                    defaults={"texto_respuesta": texto, "tipo": pregunta.tipo}
                )
                if not created:
                    respuesta.texto_respuesta = texto
                    respuesta.save()

        if evidencia_form.is_valid() and evidencia_form.cleaned_data.get('archivo'):
            archivo = evidencia_form.cleaned_data['archivo']
            nombre= evidencia_form.cleaned_data.get('nombre') or archivo.name

            def detectar_tipo_archivo(nombre):
                ext = nombre.split('.')[-1].lower()
                if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                    return 'imagen'
                if ext in ['mp4', 'mpeg', 'avi', 'mov']:
                    return 'video'
                if ext in ['mp3', 'wav', 'ogg', 'm4a']:
                    return 'audio'
                if ext in ['pdf', 'doc', 'docx', 'txt']:
                    return 'documento'
                return 'otro'

            Multimedia.objects.create(
                incidencia=incidencia,
                nombre=nombre,
                archivo = archivo,
                tipo=detectar_tipo_archivo(archivo.name),  # ✔️ Mejorado
                formato=archivo.name.split('.')[-1],
                tamanio=archivo.size,
                encuesta=encuesta
                )
            messages.success(request, "Encuesta enviada correctamente.")
            return redirect(request.path)
           
    return render(request, "territorial_app/responder_encuesta.html", {
        "encuesta": encuesta,
        "preguntas": preguntas,
        "incidencia":incidencia,
        "form":evidencia_form,
    })

@login_required
@admin_o_territorial
def encuesta_editar(request, pk):
    """
    Edita una encuesta existente.
    Permite:
      - Modificar preguntas manuales existentes
      - Agregar nuevas preguntas
      - Eliminar preguntas
    No se pueden editar preguntas base.
    """
    encuesta = get_object_or_404(Encuesta, pk=pk)

    if encuesta.estado:
        messages.error(request, "No se puede editar una encuesta activa. Debes desactivarla primero.")
        return redirect("territorial_app:encuesta_detalle", encuesta_id=pk)

    # Solo preguntas manuales
    preguntas_manual = list(encuesta.preguntaencuesta_set.filter(tipo='texto').order_by('id'))

    # Creamos formset con opción de eliminar
    PreguntaFormSet = formset_factory(PreguntaEncuestaForm, extra=1, can_delete=True)

    if request.method == 'POST':
        encuesta_form = EncuestaForm(request.POST, instance=encuesta)  
        formset = PreguntaFormSet(request.POST, prefix='manual')

        if encuesta_form.is_valid() and formset.is_valid():
            encuesta_form.save()
            # Guardar/Actualizar preguntas existentes
            for i, f in enumerate(formset.cleaned_data):
                if not f:
                    continue
                if f.get('DELETE'):
                    # Si está marcado para borrar, eliminamos la pregunta correspondiente si existe
                    if i < len(preguntas_manual):
                        preguntas_manual[i].delete()
                else:
                    if i < len(preguntas_manual):
                        # Actualizar pregunta existente
                        pregunta = preguntas_manual[i]
                        pregunta.texto_pregunta = f['texto_pregunta']
                        pregunta.save()
                    else:
                        # Crear nueva pregunta manual
                        if f.get('texto_pregunta'):
                            PreguntaEncuesta.objects.create(
                                encuesta=encuesta,
                                texto_pregunta=f['texto_pregunta'],
                                tipo='texto'
                            )
            messages.success(request, f"Encuesta '{encuesta.titulo}' actualizada correctamente.")
            return redirect("territorial_app:encuesta_detalle", encuesta_id=encuesta.id)
    else:
        # Inicializamos el formset con preguntas existentes
        initial_data = [{'texto_pregunta': p.texto_pregunta} for p in preguntas_manual]
        formset = PreguntaFormSet(initial=initial_data, prefix='manual')
        encuesta_form = EncuestaForm(instance=encuesta)

    return render(request, "territorial_app/encuesta_form.html", {
        'encuesta_form': encuesta_form,
        'formset': formset,
        'encuesta': encuesta,
        'modo': 'editar'
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
        return redirect("territorial_app:encuesta_detalle", encuesta_id=pk)
    
    if request.method == "POST":
        titulo = encuesta.titulo
        encuesta.delete()
        messages.success(request, f"Encuesta '{titulo}' eliminada correctamente.")
        return redirect("territorial_app:encuestas_lista")
    
    return render(request, "territorial_app/encuesta_eliminar.html", {"encuesta": encuesta})

#Funciones para manejar evidencias

@login_required
@admin_o_territorial
@admin_territorial_cuadrilla
def evidencia_subir(request, encuesta_id):
    """
    Sube una evidencia (imagen, video, audio, documento) a una encuesta.
    Usa AJAX para subida dinámica sin recargar la página.
    """
    encuesta = get_object_or_404(Encuesta, pk=encuesta_id)
    if encuesta.estado:
        messages.error(request, "No se puede subir evidencia en una encuesta activa. Debes desactivarla primero.")
        return redirect("territorial_app:encuesta_detalle", encuesta_id=encuesta_id)
    
    incidencia = encuesta.incidencia_set.first()

    if incidencia is None:
        messages.error(
            request,
            "No se puede subir evidencia porque esta encuesta no tiene una incidencia asociada."
        )
        return redirect("territorial_app:encuesta_detalle", encuesta_id=encuesta_id)
    
    if request.method == 'POST':
        form = EvidenciaForm(request.POST, request.FILES)
        
        if form.is_valid():
            evidencia = form.save(commit=False)
            evidencia.encuesta = encuesta
            
            # Si hay una incidencia asociada, también la vinculamos
            incidencia = encuesta.incidencia_set.first()
            if incidencia:
                evidencia.incidencia = incidencia
            
            evidencia.save()
            
            # Respuesta para AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Evidencia subida correctamente',
                    'evidencia': {
                        'id': evidencia.id,
                        'nombre': evidencia.nombre,
                        'tipo': evidencia.tipo,
                        'formato': evidencia.formato,
                        'url': evidencia.archivo.url,
                        'icono': evidencia.get_icono(),
                        'tamanio': evidencia.tamanio,
                    }
                })
            
            messages.success(request, f'Evidencia "{evidencia.nombre}" subida correctamente.')
            return redirect('territorial_app:encuesta_detalle', encuesta_id=encuesta.id)
        else:
            # Errores del formulario
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                errors = {}
                for field, error_list in form.errors.items():
                    errors[field] = [str(e) for e in error_list]
                return JsonResponse({
                    'success': False,
                    'errors': errors
                }, status=400)
            
            messages.error(request, 'Error al subir la evidencia. Verifica el formulario.')
    
    return redirect('territorial_app:encuesta_detalle', encuesta_id=encuesta.id)


@login_required
@admin_o_territorial
def evidencia_eliminar(request, evidencia_id):
    """
    Elimina una evidencia.
    """
    evidencia = get_object_or_404(Multimedia, pk=evidencia_id)
    encuesta_id = evidencia.encuesta.id if evidencia.encuesta else None
    
    if request.method == 'POST':
        nombre = evidencia.nombre
        
        # Eliminar archivo físico
        if evidencia.archivo:
            try:
                if os.path.isfile(evidencia.archivo.path):
                    os.remove(evidencia.archivo.path)
            except Exception as e:
                print(f"Error al eliminar archivo físico: {e}")
        
        evidencia.delete()
        
        # Respuesta para AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Evidencia "{nombre}" eliminada correctamente'
            })
        
        messages.success(request, f'Evidencia "{nombre}" eliminada correctamente.')
        
        if encuesta_id:
            return redirect('territorial_app:encuesta_detalle', encuesta_id=encuesta_id)
    
    return redirect('territorial_app:encuestas_lista')