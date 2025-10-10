from core.models import Incidencia, Departamento
from django.shortcuts import render, redirect, get_object_or_404
from .forms import IncidenciaForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.utils import solo_admin

# ----------------- Ayudantes de filtrado por rol -----------------
def _roles_usuario(user):
    return set(user.groups.values_list("name", flat=True))

def _filtrar_por_rol(qs, user):
    """
    Restringe el queryset según el rol del usuario.
    Reglas:
      - Admin (is_superuser) o grupo 'Administrador' y 'Dirección' ven todo.
      - 'Departamento' ve todo.
      - 'Jefe de Cuadrilla' -> solo pendiente y en_proceso.
      - 'Territorial' -> solo pendiente.
      - Sin grupo -> solo incidencias asociadas a su email.
    """
    roles = _roles_usuario(user)

    if user.is_superuser or "Administrador" in roles or "Dirección" in roles:
        return qs

    if "Departamento" in roles:
        return qs

    if "Jefe de Cuadrilla" in roles:
        return qs.filter(estado__in=["pendiente", "en_proceso"])

    if "Territorial" in roles:
        return qs.filter(estado="pendiente")

    # Sin rol: solo ve las suyas (por email)
    return qs.filter(email_usuario=user.email)


# ----------------- LISTA / DETALLE (abierto a usuarios logueados) -----------------
@login_required
def incidencias_lista(request):
    q = (request.GET.get("q") or "").strip()
    estado = request.GET.get("estado")  # 'pendiente' | 'en_proceso' | 'resuelto' | None
    departamento_id = request.GET.get("departamento") #nuevo filtro
    qs = Incidencia.objects.all().order_by("-creadoEl")

    # Filtro por texto
    if q:
        qs = qs.filter(titulo__icontains=q)

    # Filtro por rol
    qs = _filtrar_por_rol(qs, request.user)

    # Filtro por estado
    estados_validos = [e[0] for e in IncidenciaForm.ESTADO_CHOICES]
    if estado in estados_validos:
        qs = qs.filter(estado=estado)
    
    #filtro por departamento
    if departamento_id:
        qs = qs.filter(departamento_id =departamento_id)

    #etiquetas de colores para cada estado
    ESTADOS_COLORES = {
    "pendiente": "secondary",
    "en proceso": "warning",
    "finalizada": "success",
    "validada": "info",
    "rechazada": "danger",
}

    ctx = {
        "incidencias": qs,
        "q": q,
        "estado_seleccionado": estado,
        "departamentos": Departamento.objects.all(),
        "estados_colores " : ESTADOS_COLORES,
    }
    return render(request, "incidencias/incidencias_lista.html", ctx)

@login_required
def incidencia_detalle(request, pk):
    incidencia = get_object_or_404(Incidencia, pk=pk)
    # protección de acceso al detalle según rol
    visible = _filtrar_por_rol(Incidencia.objects.filter(pk=pk), request.user).exists()
    if not visible:
        messages.error(request, "No tienes permisos para ver esta incidencia.")
        return redirect("incidencias:incidencias_lista")
    return render(request, "incidencias/incidencia_detalle.html", {"obj": incidencia})


# ----------------- CRUD (solo administrador) -----------------
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
def incidencia_eliminar(request, pk):
    obj = get_object_or_404(Incidencia, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Incidencia eliminada correctamente.")
        return redirect("incidencias:incidencias_lista")
    return render(request, "incidencias/incidencia_eliminar.html", {"obj": obj})
