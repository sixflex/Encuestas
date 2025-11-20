from core.models import Incidencia, Departamento, JefeCuadrilla, Multimedia, TipoIncidencia#cambio barbara
from django.shortcuts import render, redirect, get_object_or_404
from .forms import IncidenciaForm, SubirEvidenciaForm #cambio barbraa
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.utils import solo_admin

#Cambio barbara
from django.http import JsonResponse 
from django.core.mail import send_mail
from django.conf import settings
from django.core.files.storage import default_storage
import os
from datetime import datetime


# ----------------- intento de API para cargar cuadrillas por departamento -----------------
@login_required
def cuadrillas_por_departamento(request, departamento_id):
    """Vista AJAX para cargar las cuadrillas de un departamento."""
    cuadrillas = JefeCuadrilla.objects.filter(departamento_id=departamento_id)
    data = [{'id': c.id, 'nombre_cuadrilla': str(c)} for c in cuadrillas]
    return JsonResponse(data, safe=False)

# ----------------- intento de API 2 sjsj para cargar tipos -----------------
@login_required
def cargar_tipos(request):
    """Vista AJAX para cargar los tipos de una categoría."""
    categoria_id = request.GET.get('categoria_id')
    if not categoria_id:
        return JsonResponse({'tipos': []})
    
    tipos = TipoIncidencia.objects.filter(
        categoria_id=categoria_id,
        activo=True
    ).values('id', 'nombre', 'prioridad_predeterminada')
    
    return JsonResponse({'tipos': list(tipos)})
#---------------------------------------
# ----------------- Ayudantes de filtrado por rol -----------------
def _roles_usuario(user):
    return set(user.groups.values_list("name", flat=True))

def _filtrar_por_rol(qs, user):
    """
    Restringe el queryset según el rol del usuario.
    Reglas:
      - Admin (is_superuser) o grupo 'Administrador' y 'Dirección' ven todo.
      - 'Departamento' ve todo.
      - 'Jefe de Cuadrilla' -> solo pendiente y en_progreso.
      - 'Territorial' -> solo pendiente.
      - Sin grupo -> solo incidencias asociadas a su email.
    """
    roles = _roles_usuario(user)

    if user.is_superuser or "Administrador" in roles or "Dirección" in roles:
        return qs
    
    
    if "Departamento" in roles:
        return qs
#-------------cambios barbara-------
    if "Jefe de Cuadrilla" in roles:
        # Filtrar todas las incidencias de las cuadrillas donde el usuario es usuario o encargado
        from core.models import JefeCuadrilla
        from django.db.models import Q
        try:
            profile = user.profile
            cuadrillas = JefeCuadrilla.objects.filter(
                Q(usuario=profile) | Q(encargado=profile)
            )
            return qs.filter(
                cuadrilla__in=cuadrillas
            )
        except:
            return qs.none()
        #return qs.filter(estado__in=["pendiente", "en_progreso"])

    if "Territorial" in roles:
        return qs
#---------------------------------------------------------------------------------------------------
    # Sin rol: solo ve las suyas (por email)
    return qs.filter(email_usuario=user.email)


# ----------------- LISTA / DETALLE (abierto a usuarios logueados) -----------------
@login_required
def incidencias_lista(request):
    q = (request.GET.get("q") or "").strip()
    estado = request.GET.get("estado")  # 'pendiente' | 'en_progreso' | 'resuelto' | None
    departamento_id = request.GET.get("departamento") #nuevo filtro
    tipo_id = request.GET.get("tipo_id")#nuevo
    tipos = TipoIncidencia.objects.all()#nuevo

    qs = Incidencia.objects.all().order_by("-creadoEl")

    # Filtro por texto
    if q:
        qs = qs.filter(titulo__icontains=q)

    # Filtro por rol
    qs = _filtrar_por_rol(qs, request.user)

    # Filtro por estado
    estados_validos = [e[0] for e in Incidencia.ESTADO_CHOICES]
    if estado in estados_validos:
        qs = qs.filter(estado=estado)
    
    #filtro por departamento
    if departamento_id:
        qs = qs.filter(departamento_id =departamento_id)
    
    # Filtro por tipo de incidencia
    if tipo_id:
        qs = qs.filter(tipo_incidencia_id=tipo_id)

    #etiquetas de colores para cada estado
    ESTADOS_COLORES = {
    "Pendiente": "secondary",
    "En progreso": "warning",
    "Completada": "success",
    "validada": "info",
    "rechazada": "danger",
}
# ---Filtrar por rol del usuario ---
    user = request.user
    grupos = list(user.groups.values_list("name", flat=True))

    is_territorial = "Territorial" in grupos
    is_departamento = "Departamento" in grupos
    is_jefe = "Jefe de Cuadrilla" in grupos
    is_direccion = "Dirección" in grupos
    is_admin = "Administrador" in grupos or user.is_superuser
    departamento_nombre = ""
    if departamento_id:
        try:
            departamento_nombre = Departamento.objects.get(id=departamento_id).nombre_departamento
        except Departamento.DoesNotExist:
            departamento_nombre = ""

    ctx = {
        "incidencias": qs,
        "q": q,
        "estado_seleccionado": estado,
        "departamentos": Departamento.objects.all(),
        "departamento_seleccionado": departamento_id,
        "departamento_nombre": departamento_nombre,
        "estados_colores" : ESTADOS_COLORES,
        "is_territorial": is_territorial,
        "is_departamento": is_departamento,
        "is_jefe": is_jefe,
        "is_direccion": is_direccion,
        "is_admin": is_admin,
        "tipos": tipos,
        "tipo_seleccionado": tipo_id, 
    }

    return render(request, "incidencias/incidencias_lista.html", ctx)
    
@login_required
def incidencia_detalle(request, pk):
    incidencia = get_object_or_404(Incidencia, pk=pk)

    visible = _filtrar_por_rol(Incidencia.objects.filter(pk=pk), request.user).exists()
    if not visible:
        messages.error(request, "No tienes permisos para ver esta incidencia.")
        return redirect("incidencias:incidencias_lista")

    encuesta = getattr(incidencia, "encuesta", None)
    preguntas_con_respuestas = []

    if encuesta:
        preguntas = encuesta.preguntaencuesta_set.all().prefetch_related("respuestas")
        for p in preguntas:
            respuesta = p.respuestas.first()
            preguntas_con_respuestas.append({
                "texto_pregunta": p.texto_pregunta,
                "respuesta": respuesta.texto_respuesta if respuesta else "No respondida"
            })

    contexto = {
        "obj": incidencia,
        "encuesta": encuesta,
        "preguntas_con_respuestas": preguntas_con_respuestas,
    }

    return render(request, "incidencias/incidencia_detalle.html", contexto)

# ----------------- CRUD (solo administrador) -----------------
@login_required
def incidencia_crear(request):
#  VERIFICACIÓN PARA BLOQUEAR A 'DIRECCIÓN'
    roles = _roles_usuario(request.user)
    if "Dirección" in roles and not request.user.is_superuser:
        messages.error(request, "El rol 'Dirección' no tiene permisos para crear incidencias.")
        return redirect("incidencias:incidencias_lista") # Redirigir a la lista

    # 2. El resto de la vista sigue igual
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
def incidencia_editar(request, pk):
    incidencia = get_object_or_404(Incidencia, pk=pk)
    estado_anterior = incidencia.estado
    motivo_rechazo = request.POST.get('motivo_rechazo')
    roles = set(request.user.groups.values_list("name", flat=True))

    if request.method == "POST":
        form = IncidenciaForm(request.POST, instance=incidencia)
        if form.is_valid():
            nueva_incidencia = form.save(commit=False)
            nuevo_estado = nueva_incidencia.estado
            
            puede_guardar = False
            
            # 1. ADMIN/SUPERUSER: Poder absoluto
            if request.user.is_superuser or 'Administrador' in roles:
                puede_guardar = True
            
            # 2. TERRITORIAL:
            elif 'Territorial' in roles:
                # Puede editar si está Pendiente/Rechazada. Completada -> Validada/Rechazada
                if estado_anterior in ['Pendiente', 'Rechazada']:
                    puede_guardar = True
                elif estado_anterior == 'Completada' and nuevo_estado in ['Validada', 'Rechazada']:
                    puede_guardar = True
            
            # 3. DEPARTAMENTO:
            elif 'Departamento' in roles:
                # Transición: Pendiente -> En Progreso o Rechazada. También puede editar si está Rechazada.
                if estado_anterior in ['Pendiente', 'Rechazada']:
                    if nuevo_estado in ['En Progreso', 'Rechazada', estado_anterior]:
                         puede_guardar = True
                    else:
                         messages.error(request, f"Departamento solo puede cambiar a 'En Progreso' o 'Rechazada' desde Pendiente/Rechazada.")
                         return redirect("incidencias:incidencias_lista")
                
            # 4. CUADRILLA:
            elif 'Jefe de Cuadrilla' in roles:
                # Transición: En Progreso -> Completada
                if estado_anterior == 'En Progreso' and nuevo_estado == 'Completada':
                    puede_guardar = True
            
            # Si el estado NO cambia, y el usuario tiene permiso de "turno", permitir guardar datos.
            if estado_anterior == nuevo_estado:
                 puede_guardar = True
            
            if not puede_guardar:
                messages.error(request, f"No tienes permisos para cambiar el estado de '{estado_anterior}' a '{nuevo_estado}' o editar en esta etapa.")
                return redirect("incidencias:incidencias_lista")
            
            # Manejo de Rechazo (Actualiza el estado de la incidencia y la desasigna si es necesario)
            if nuevo_estado == 'Rechazada':
                if estado_anterior == 'Completada' and 'Territorial' in roles:
                    # Rechazo de Territorial: Devuelve a Pendiente, desasigna cuadrilla y avisa a Depto
                    nueva_incidencia.estado = 'Pendiente'
                    nueva_incidencia.cuadrilla = None
                    messages.warning(request, "Incidencia rechazada y devuelta a Pendiente para reasignación.")
                elif estado_anterior == 'Pendiente' and 'Departamento' in roles:
                    # Rechazo de Depto: Se queda Pendiente, avisa a Territorial para reasignar a otro Depto
                    nueva_incidencia.estado = 'Pendiente'
                    messages.warning(request, "Incidencia rechazada por el Departamento.")


            if nueva_incidencia.estado == 'Rechazada' and motivo_rechazo:
                nueva_incidencia.motivo_rechazo = motivo_rechazo
            
            nueva_incidencia.save()

            if nueva_incidencia.estado != estado_anterior:
                # Lógica de Notificación por Correo
                departamento = nueva_incidencia.departamento
                destinatario = "soporte@municipalidad.local"
                if departamento and departamento.encargado and departamento.encargado.user.email:
                    destinatario = departamento.encargado.user.email
                
                remitente = request.user.email if request.user.email else "no-reply@municipalidad.local"
                asunto = f"[Notificación] Estado actualizado: {nueva_incidencia.titulo}"
                cuerpo = f"El estado cambió de {estado_anterior} a {nueva_incidencia.estado}."

                try:
                    send_mail(asunto, cuerpo, remitente, [destinatario], fail_silently=True)
                except:
                    pass 

                messages.success(request, f"Incidencia actualizada a '{nueva_incidencia.estado}'.")
            else:
                messages.success(request, "Incidencia actualizada correctamente.")

            return redirect("incidencias:incidencias_lista")
    else:
        form = IncidenciaForm(instance=incidencia)

    return render(request, "incidencias/incidencia_form.html", {"form": form})
#----------cambios barbara, nuevo incidencia_editar
@login_required
def incidencia_editar(request, pk):
    incidencia = get_object_or_404(Incidencia, pk=pk)
    estado_anterior = incidencia.estado
    motivo_rechazo = request.POST.get('motivo_rechazo')
    roles = set(request.user.groups.values_list("name", flat=True))

    if request.method == "POST":
        form = IncidenciaForm(request.POST, instance=incidencia)
        if form.is_valid():
            nuevo_estado = form.cleaned_data['estado']
            
            # Validar permisos según el rol y el cambio de estado
            puede_cambiar = False
            
            if request.user.is_superuser or 'Administrador' in roles:
                puede_cambiar = True
            elif 'Territorial' in roles:
                # Territorial solo puede crear (pendiente) y validar/rechazar completadas
                if estado_anterior == 'Completada' and nuevo_estado in ['Validada', 'Rechazada']:
                    puede_cambiar = True
            elif 'Departamento' in roles:
                # Departamento solo puede poner en proceso las pendientes
                if estado_anterior == 'Pendiente' and nuevo_estado == 'En Progreso':
                    puede_cambiar = True
            elif 'Jefe de Cuadrilla' in roles:
                # Cuadrilla solo puede finalizar las que están en proceso
                if estado_anterior == 'En Progreso' and nuevo_estado == 'Completada':
                    puede_cambiar = True
                    
            if not puede_cambiar:
                messages.error(request, "No tienes permisos para realizar este cambio de estado.")
                return redirect("incidencias:incidencias_lista")
            
            incidencia = form.save(commit=False)
            
            # Si se está rechazando la incidencia, guardar el motivo
            if incidencia.estado == 'Rechazada' and motivo_rechazo:
                incidencia.motivo_rechazo = motivo_rechazo
            
            incidencia.save()

            if incidencia.estado != estado_anterior:
                departamento = incidencia.departamento
                if departamento and departamento.encargado and departamento.encargado.user.email:
                    destinatario = departamento.encargado.user.email
                else:
                    destinatario = "soporte@municipalidad.local"

                remitente = (
                    request.user.email
                    if request.user.email
                    else "no-reply@municipalidad.local"
                )

                asunto = f"[Notificación] Estado actualizado de incidencia: {incidencia.titulo}"
                cuerpo = (
                    f"Estimado/a {departamento.encargado},\n\n"
                    f"El usuario {request.user.get_full_name() or request.user.username} "
                    f"ha cambiado el estado de la incidencia '{incidencia.titulo}'.\n\n"
                    f"Estado anterior: {estado_anterior}\n"
                    f"Nuevo estado: {incidencia.estado}\n\n"
                    f"Departamento: {departamento.nombre_departamento if departamento else 'No asignado'}\n"
                    f"Descripción: {incidencia.descripcion}\n"
                    f"Fecha del cambio: {incidencia.actualizadoEl.strftime('%d-%m-%Y %H:%M')}\n\n"
                    "Saludos cordiales,\n"
                    "Sistema Municipal de Incidencias"
                )

                send_mail(
                    asunto,
                    cuerpo,
                    remitente,
                    [destinatario],
                    fail_silently=False,
                )

                messages.success(
                    request,
                    f"Incidencia actualizada. Se notificó a {departamento.encargado} ({destinatario})."
                )
            else:
                messages.success(request, "Incidencia actualizada correctamente.")

            return redirect("incidencias:incidencias_lista")
    else:
        form = IncidenciaForm(instance=incidencia)

    return render(request, "incidencias/incidencia_form.html", {"form": form})
#-----------------------------------------------------------

@login_required
@solo_admin
def incidencia_eliminar(request, pk):
    obj = get_object_or_404(Incidencia, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Incidencia eliminada correctamente.")
        return redirect("incidencias:incidencias_lista")
    return render(request, "incidencias/incidencia_eliminar.html", {"obj": obj})


#-----------CAMBIOS BARBARAA
# ----------------- SUBIR EVIDENCIAAA -----------------
@login_required
def subir_evidencia(request, pk):
    """
    Vista para que el Jefe de Cuadrilla asignado suba evidencia y finalice la incidencia.
    Solo la cuadrilla asignada puede acceder.
    """
    incidencia = get_object_or_404(Incidencia, pk=pk)
    roles = set(request.user.groups.values_list("name", flat=True))
    
    # DEBUG: Agregar información de depuración
    print(f"\n{'='*60}")
    print(f"DEBUG - SUBIR EVIDENCIA")
    print(f"Usuario: {request.user.username}")
    print(f"Grupos del usuario: {list(roles)}")
    print(f"Es superuser: {request.user.is_superuser}")
    print(f"Incidencia: #{incidencia.id} - {incidencia.titulo}")
    print(f"Estado incidencia: {incidencia.estado}")
    print(f"Cuadrilla asignada: {incidencia.cuadrilla}")
    try:
        print(f"Profile del usuario: {request.user.profile}")
        if incidencia.cuadrilla:
            print(f"Usuario de cuadrilla: {incidencia.cuadrilla.usuario}")
            print(f"Encargado de cuadrilla: {incidencia.cuadrilla.encargado}")
            print(f"¿Coincide con usuario?: {incidencia.cuadrilla.usuario == request.user.profile}")
            print(f"¿Coincide con encargado?: {incidencia.cuadrilla.encargado == request.user.profile}")
    except Exception as e:
        print(f"ERROR al obtener profile: {e}")
    print(f"{'='*60}\n")
    
    # Validación 1: Solo usuarios con rol "Jefe de Cuadrilla", "Cuadrilla" o "Administrador" pueden acceder
    if not (request.user.is_superuser or "Jefe de Cuadrilla" in roles or "Cuadrilla" in roles or "Administrador" in roles):
        messages.error(request, f"No tienes permisos para subir evidencia. Tus grupos son: {list(roles)}")
        return redirect("incidencias:incidencias_lista")
    
    # Validación 2: Solo la cuadrilla asignada puede subir evidencia
    if not request.user.is_superuser and "Administrador" not in roles:
        if not incidencia.cuadrilla:
            messages.error(request, "Esta incidencia no tiene cuadrilla asignada.")
            return redirect("incidencias:incidencias_lista")
        # Verificar que el usuario pertenece a la cuadrilla asignada
        try:
            usuario_es_de_cuadrilla = (
                incidencia.cuadrilla.usuario == request.user.profile or
                incidencia.cuadrilla.encargado == request.user.profile
            )
        except Exception as e:
            messages.error(request, f"Error al verificar perfil: {e}. Contacta al administrador.")
            return redirect("incidencias:incidencias_lista")
            
        if not usuario_es_de_cuadrilla:
            messages.error(
                request,
                f"Solo la cuadrilla '{incidencia.cuadrilla.nombre_cuadrilla}' puede subir evidencia. "
                f"Tu perfil no coincide con el usuario o encargado de esta cuadrilla."
            )
            return redirect("incidencias:incidencias_lista")
    
    # Validación 3: Solo se puede subir evidencia si está en estado "en_progreso"
    if incidencia.estado != "En Progreso":
        messages.warning(
            request,
            f"Solo se puede subir evidencia cuando la incidencia está 'En proceso'. Estado actual: {incidencia.estado}"
        )
        return redirect("incidencias:incidencia_detalle", pk=pk)
    
    if request.method == "POST":
        form = SubirEvidenciaForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = form.cleaned_data['archivo']
            nombre = form.cleaned_data.get('nombre') or archivo.name
            
            # Crear directorio si no existe
            upload_path = 'evidencias/'
            os.makedirs(os.path.join(settings.MEDIA_ROOT, upload_path), exist_ok=True)
            
            # Guardar archivo con un nombre único
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_archivo = f"{timestamp}_{archivo.name}"
            ruta_completa = os.path.join(upload_path, nombre_archivo)
            ruta_guardada = default_storage.save(ruta_completa, archivo)
            
            # Crear registro en Multimedia
            multimedia = Multimedia.objects.create(
                nombre=nombre,
                url=settings.MEDIA_URL + ruta_guardada,
                tipo=archivo.content_type.split('/')[0],
                formato=archivo.name.split('.')[-1],
                incidencia=incidencia
            )
            
            # NO cambiar automáticamente a Completada - permitir subir múltiples evidencias
            # La cuadrilla debe finalizar manualmente cuando termine
            
            messages.success(
                request,
                f"Evidencia '{nombre}' subida correctamente. Puedes subir más evidencias o finalizar la incidencia cuando termines."
            )
            return redirect("incidencias:incidencia_detalle", pk=pk)
    else:
        form = SubirEvidenciaForm()
    
    ctx = {
        'form': form,
        'incidencia': incidencia
    }
    return render(request, "incidencias/subir_evidencia.html", ctx)


# ----------------- FINALAIZAR INCIDENCIAAS , esto esta en territorial de nuevo-----------------
@login_required
def finalizar_incidencia(request, pk):
    """
    Vista para que la cuadrilla marque una incidencia como Completada después de subir evidencias.
    """
    incidencia = get_object_or_404(Incidencia, pk=pk)
    roles = set(request.user.groups.values_list("name", flat=True))
    
    # Validación 1: Solo cuadrillas o admin
    if not (request.user.is_superuser or "Jefe de Cuadrilla" in roles or "Cuadrilla" in roles or "Administrador" in roles):
        messages.error(request, "No tienes permisos para finalizar incidencias.")
        return redirect("incidencias:incidencias_lista")
    
    # Validación 2: Solo la auadrilla asignada
    if not request.user.is_superuser and "Administrador" not in roles:
        if not incidencia.cuadrilla:
            messages.error(request, "Esta incidencia no tiene cuadrilla asignada.")
            return redirect("incidencias:incidencias_lista")
        
        try:
            usuario_es_de_cuadrilla = (
                incidencia.cuadrilla.usuario == request.user.profile or
                incidencia.cuadrilla.encargado == request.user.profile
            )
        except Exception as e:
            messages.error(request, f"Error al verificar perfil: {e}")
            return redirect("incidencias:incidencias_lista")
            
        if not usuario_es_de_cuadrilla:
            messages.error(request, f"Solo la cuadrilla '{incidencia.cuadrilla.nombre_cuadrilla}' puede finalizar esta incidencia.")
            return redirect("incidencias:incidencias_lista")
    
    # Validación 3: Debe estar en "en_progreso"
    if incidencia.estado != "en_progreso":
        messages.warning(request, f"Solo se pueden finalizar incidencias en estado 'En proceso'. Estado actual: {incidencia.estado}")
        return redirect("incidencias:incidencia_detalle", pk=pk)
    
    # Validación 4: Debe tener al menos una evidencia
    if not incidencia.multimedias.exists():
        messages.error(request, "Debes subir al menos una evidencia antes de finalizar la incidencia.")
        return redirect("incidencias:subir_evidencia", pk=pk)
    
    # Finalizar incidencia
    incidencia.estado = "Completada"
    incidencia.save()
    
    messages.success(
        request,
        f"¡Incidencia Completada correctamente! El territorial ahora puede validar o rechazar el trabajo realizado."
    )
    return redirect("incidencias:incidencia_detalle", pk=pk)
