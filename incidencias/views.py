# incidencias/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.mail import send_mail
from datetime import datetime
import os

from core.models import (
    Incidencia,
    Departamento,
    JefeCuadrilla,
    Multimedia,
    TipoIncidencia,
)
from .forms import (
    IncidenciaForm,
    SubirEvidenciaForm,
    TipoIncidenciaForm,
    PreguntaDefaultTipoFormSet,
)

# =====================================================================================
# TIPOS DE INCIDENCIA + PREGUNTAS DEFAULT (formset con prefix="pregs")
# =====================================================================================

def tipo_lista(request):
    tipos = TipoIncidencia.objects.all().order_by("id")
    return render(request, "tipo/tipo_lista.html", {"tipos": tipos})


def tipo_crear(request):
    prefix = "pregs"
    if request.method == "POST":
        form = TipoIncidenciaForm(request.POST)
        formset = PreguntaDefaultTipoFormSet(request.POST, prefix=prefix)
        if form.is_valid() and formset.is_valid():
            tipo = form.save()
            formset.instance = tipo
            formset.save()
            return redirect("incidencias:tipo_lista")
    else:
        form = TipoIncidenciaForm()
        formset = PreguntaDefaultTipoFormSet(prefix=prefix)

    return render(request, "incidencias/tipo_form.html", {
        "form": form,
        "formset": formset,
    })


def tipo_editar(request, pk):
    prefix = "pregs"
    tipo = get_object_or_404(TipoIncidencia, pk=pk)
    if request.method == "POST":
        form = TipoIncidenciaForm(request.POST, instance=tipo)
        formset = PreguntaDefaultTipoFormSet(request.POST, instance=tipo, prefix=prefix)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, "Tipo de incidencia y preguntas actualizadas.")
            return redirect("incidencias:tipo_lista")
    else:
        form = TipoIncidenciaForm(instance=tipo)
        formset = PreguntaDefaultTipoFormSet(instance=tipo, prefix=prefix)

    return render(request, "incidencias/tipo_form.html", {
        "form": form,
        "formset": formset,
        "formset_total_name": f"{formset.prefix}-TOTAL_FORMS",
    })


def tipo_eliminar(request, pk):
    tipo = get_object_or_404(TipoIncidencia, pk=pk)
    if request.method == "POST":
        tipo.delete()
        messages.success(request, "Tipo de incidencia eliminado.")
        return redirect("incidencias:tipo_lista")
    return render(request, "tipo/tipo_eliminar.html", {"obj": tipo})


# =====================================================================================
# API AUX: Cargar cuadrillas según departamento (AJAX)
# =====================================================================================

@login_required
def cuadrillas_por_departamento(request, departamento_id):
    cuadrillas = JefeCuadrilla.objects.filter(departamento_id=departamento_id)
    data = [{"id": c.id, "nombre_cuadrilla": str(c)} for c in cuadrillas]
    return JsonResponse(data, safe=False)


# =====================================================================================
# Helpers de rol y filtros
# =====================================================================================

def _roles_usuario(user):
    return set(user.groups.values_list("name", flat=True))

def _filtrar_por_rol(qs, user):
    """
    Reglas:
      - Admin (is_superuser) o grupo 'Administrador' o 'Dirección' ven todo.
      - 'Departamento' ve todo.
      - 'Jefe de Cuadrilla' -> incidencias de sus cuadrillas (como usuario o encargado).
      - 'Territorial' -> incidencias de sus cuadrillas en estado 'Pendiente'.
      - Sin grupo -> incidencias asociadas a su email (si lo usas).
    """
    roles = _roles_usuario(user)

    if user.is_superuser or "Administrador" in roles or "Dirección" in roles:
        return qs

    if "Departamento" in roles:
        return qs

    if "Jefe de Cuadrilla" in roles:
        try:
            profile = user.profile
            from django.db.models import Q
            cuadrillas = JefeCuadrilla.objects.filter(Q(usuario=profile) | Q(encargado=profile))
            return qs.filter(cuadrilla__in=cuadrillas)
        except Exception:
            return qs.none()

    if "Territorial" in roles:
        try:
            profile = user.profile
            from django.db.models import Q
            cuadrillas = JefeCuadrilla.objects.filter(Q(usuario=profile) | Q(encargado=profile))
            return qs.filter(cuadrilla__in=cuadrillas, estado="Pendiente")
        except Exception:
            return qs.none()

    # fallback: por email del usuario (ajusta si tu modelo no tiene este campo)
    return qs.filter(correo_vecino=user.email)


# =====================================================================================
# LISTA / DETALLE
# =====================================================================================

@login_required
def incidencias_lista(request):
    q = (request.GET.get("q") or "").strip()
    estado = request.GET.get("estado")  # Debe ser uno de Incidencia.ESTADO_CHOICES
    departamento_id = request.GET.get("departamento")
    tipo_id = request.GET.get("tipo")

    qs = Incidencia.objects.all().order_by("-creadoEl")

    if q:
        qs = qs.filter(titulo__icontains=q)

    qs = _filtrar_por_rol(qs, request.user)

    estados_validos = [e[0] for e in Incidencia.ESTADO_CHOICES]
    if estado in estados_validos:
        qs = qs.filter(estado=estado)

    if departamento_id:
        qs = qs.filter(departamento_id=departamento_id)

    if tipo_id:
        qs = qs.filter(tipo_incidencia_id=tipo_id)

    ESTADOS_COLORES = {
        "Pendiente": "secondary",
        "En Progreso": "warning",
        "Completada": "success",
        "Validada": "info",
        "Rechazada": "danger",
    }

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

    tipos = TipoIncidencia.objects.all()

    ctx = {
        "incidencias": qs,
        "q": q,
        "estado_seleccionado": estado,
        "departamentos": Departamento.objects.all(),
        "departamento_seleccionado": departamento_id,
        "departamento_nombre": departamento_nombre,
        "estados_colores": ESTADOS_COLORES,
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
    return render(request, "incidencias/incidencia_detalle.html", {"obj": incidencia})


# =====================================================================================
# CRUD INCIDENCIA
# =====================================================================================

@login_required
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
def incidencia_editar(request, pk):
    """
    Reglas de transición/permiso basadas en ESTADO_CHOICES:
      Pendiente -> En Progreso (Departamento)
      En Progreso -> Completada (Jefe de Cuadrilla)
      Completada -> Validada/Rechazada (Territorial)
      Validada -> Pendiente (Administrador) [opcional]
    """
    incidencia = get_object_or_404(Incidencia, pk=pk)
    estado_anterior = incidencia.estado
    motivo_rechazo = request.POST.get('motivo_rechazo')
    roles = set(request.user.groups.values_list("name", flat=True))

    if request.method == "POST":
        form = IncidenciaForm(request.POST, instance=incidencia)
        if form.is_valid():
            nuevo_estado = form.cleaned_data['estado']

            puede_cambiar = False
            if request.user.is_superuser or 'Administrador' in roles:
                puede_cambiar = True
            elif 'Territorial' in roles:
                if estado_anterior == 'Completada' and nuevo_estado in ['Validada', 'Rechazada']:
                    puede_cambiar = True
            elif 'Departamento' in roles:
                if estado_anterior == 'Pendiente' and nuevo_estado == 'En Progreso':
                    puede_cambiar = True
            elif 'Jefe de Cuadrilla' in roles:
                if estado_anterior == 'En Progreso' and nuevo_estado == 'Completada':
                    puede_cambiar = True

            if not puede_cambiar:
                messages.error(request, "No tienes permisos para realizar este cambio de estado.")
                return redirect("incidencias:incidencias_lista")

            incidencia = form.save(commit=False)

            if incidencia.estado == 'Rechazada' and motivo_rechazo:
                incidencia.motivo_rechazo = motivo_rechazo

            incidencia.save()

            if incidencia.estado != estado_anterior:
                departamento = incidencia.departamento
                if departamento and departamento.encargado and departamento.encargado.user.email:
                    destinatario = departamento.encargado.user.email
                else:
                    destinatario = "soporte@municipalidad.local"

                remitente = request.user.email or "no-reply@municipalidad.local"

                asunto = f"[Notificación] Estado actualizado de incidencia: {incidencia.titulo}"
                cuerpo = (
                    f"Estimado/a {getattr(departamento.encargado, 'user', departamento.encargado)}\n\n"
                    f"El usuario {request.user.get_full_name() or request.user.username} "
                    f"ha cambiado el estado de la incidencia '{incidencia.titulo}'.\n\n"
                    f"Estado anterior: {estado_anterior}\n"
                    f"Nuevo estado: {incidencia.estado}\n\n"
                    f"Departamento: {departamento.nombre_departamento if departamento else 'No asignado'}\n"
                    f"Descripción: {incidencia.descripcion}\n"
                    "Saludos cordiales,\n"
                    "Sistema Municipal de Incidencias"
                )

                try:
                    send_mail(asunto, cuerpo, remitente, [destinatario], fail_silently=True)
                except Exception:
                    pass

                messages.success(
                    request,
                    f"Incidencia actualizada. Se notificó a {getattr(departamento.encargado, 'user', departamento.encargado)} ({destinatario})."
                )
            else:
                messages.success(request, "Incidencia actualizada correctamente.")

            return redirect("incidencias:incidencias_lista")
    else:
        form = IncidenciaForm(instance=incidencia)

    return render(request, "incidencias/incidencia_form.html", {"form": form})


@login_required
def incidencia_eliminar(request, pk):
    obj = get_object_or_404(Incidencia, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Incidencia eliminada correctamente.")
        return redirect("incidencias:incidencias_lista")
    return render(request, "incidencias/incidencia_eliminar.html", {"obj": obj})


# =====================================================================================
# EVIDENCIAS Y FINALIZACIÓN (ajustado a estados oficiales)
# =====================================================================================

@login_required
def subir_evidencia(request, pk):
    """
    Solo la cuadrilla asignada (o admin) puede subir evidencia.
    La incidencia debe estar en 'En Progreso'.
    """
    incidencia = get_object_or_404(Incidencia, pk=pk)
    roles = set(request.user.groups.values_list("name", flat=True))

    if not (request.user.is_superuser or "Jefe de Cuadrilla" in roles or "Cuadrilla" in roles or "Administrador" in roles):
        messages.error(request, "No tienes permisos para subir evidencia.")
        return redirect("incidencias:incidencias_lista")

    if not request.user.is_superuser and "Administrador" not in roles:
        if not incidencia.cuadrilla:
            messages.error(request, "Esta incidencia no tiene cuadrilla asignada.")
            return redirect("incidencias:incidencias_lista")
        try:
            usuario_es_de_cuadrilla = (
                incidencia.cuadrilla.usuario == request.user.profile or
                incidencia.cuadrilla.encargado == request.user.profile
            )
        except Exception:
            messages.error(request, "Error al verificar tu perfil/cargo. Contacta al administrador.")
            return redirect("incidencias:incidencias_lista")

        if not usuario_es_de_cuadrilla:
            messages.error(request, f"Solo la cuadrilla '{incidencia.cuadrilla.nombre_cuadrilla}' puede subir evidencia.")
            return redirect("incidencias:incidencias_lista")

    if incidencia.estado != "En Progreso":
        messages.warning(request, f"Solo se puede subir evidencia cuando la incidencia está 'En Progreso'. Estado actual: {incidencia.estado}")
        return redirect("incidencias:incidencia_detalle", pk=pk)

    if request.method == "POST":
        form = SubirEvidenciaForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = form.cleaned_data['archivo']
            nombre = form.cleaned_data.get('nombre') or archivo.name

            upload_dir = 'evidencias/'
            os.makedirs(os.path.join(settings.MEDIA_ROOT, upload_dir), exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_archivo = f"{timestamp}_{archivo.name}"
            ruta_relativa = os.path.join(upload_dir, nombre_archivo)
            ruta_guardada = default_storage.save(ruta_relativa, archivo)

            Multimedia.objects.create(
                nombre=nombre,
                url=settings.MEDIA_URL + ruta_guardada,
                tipo=archivo.content_type.split('/')[0],
                formato=archivo.name.split('.')[-1],
                incidencia=incidencia
            )

            messages.success(request, "Evidencia subida correctamente.")
            return redirect("incidencias:incidencia_detalle", pk=pk)
    else:
        form = SubirEvidenciaForm()

    return render(request, "incidencias/subir_evidencia.html", {"form": form, "incidencia": incidencia})


@login_required
def finalizar_incidencia(request, pk):
    """
    La cuadrilla (o admin) marca como 'Completada'.
    Debe haber al menos una evidencia y estado actual 'En Progreso'.
    """
    incidencia = get_object_or_404(Incidencia, pk=pk)
    roles = set(request.user.groups.values_list("name", flat=True))

    if not (request.user.is_superuser or "Jefe de Cuadrilla" in roles or "Cuadrilla" in roles or "Administrador" in roles):
        messages.error(request, "No tienes permisos para finalizar incidencias.")
        return redirect("incidencias:incidencias_lista")

    if not request.user.is_superuser and "Administrador" not in roles:
        if not incidencia.cuadrilla:
            messages.error(request, "Esta incidencia no tiene cuadrilla asignada.")
            return redirect("incidencias:incidencias_lista")

        try:
            usuario_es_de_cuadrilla = (
                incidencia.cuadrilla.usuario == request.user.profile or
                incidencia.cuadrilla.encargado == request.user.profile
            )
        except Exception:
            messages.error(request, "Error al verificar tu perfil/cargo.")
            return redirect("incidencias:incidencias_lista")

        if not usuario_es_de_cuadrilla:
            messages.error(request, f"Solo la cuadrilla '{incidencia.cuadrilla.nombre_cuadrilla}' puede finalizar esta incidencia.")
            return redirect("incidencias:incidencias_lista")

    if incidencia.estado != "En Progreso":
        messages.warning(request, f"Solo se puede finalizar cuando está 'En Progreso'. Estado actual: {incidencia.estado}")
        return redirect("incidencias:incidencia_detalle", pk=pk)

    if not incidencia.multimedias.exists():
        messages.error(request, "Debes subir al menos una evidencia antes de finalizar la incidencia.")
        return redirect("incidencias:subir_evidencia", pk=pk)

    incidencia.estado = "Completada"
    incidencia.save()
    messages.success(request, "¡Incidencia marcada como Completada! El Territorial puede Validar o Rechazar.")
    return redirect("incidencias:incidencia_detalle", pk=pk)
