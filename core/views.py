from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.db.models import Q
from django.views.decorators.http import require_POST
from registration.models import Profile
from .utils import solo_admin
from core.models import Incidencia, Departamento, Direccion
from .forms import UsuarioCrearForm
from django.contrib.auth.decorators import login_required

# Asegúrate de importar los formularios correctos
# from .forms import UsuarioCrearForm, UsuarioEditarForm


@solo_admin
def dashboard_admin(request):
    """Dashboard del administrador con estadísticas"""
    ultimos_usuarios = Profile.objects.order_by('-id')[:5] 
    ultimas_direcciones = Direccion.objects.order_by('-creadoEl')[:5]
    ultimos_departamentos = Departamento.objects.order_by('-creadoEl')[:5]
    ultimas_incidencias = Incidencia.objects.order_by('-creadoEl')[:5]
    total_usuarios = Profile.objects.count()
    total_incidencias_creadas = Incidencia.objects.count()
    total_incidencias_finalizadas = Incidencia.objects.filter(estado='Completada').count()

    contexto = {
        'ultimos_usuarios': ultimos_usuarios,
        'ultimas_direcciones': ultimas_direcciones,
        'ultimos_departamentos': ultimos_departamentos,
        'ultimas_incidencias': ultimas_incidencias,
        'total_usuarios': total_usuarios,
        'total_incidencias_creadas': total_incidencias_creadas,
        'total_incidencias_finalizadas': total_incidencias_finalizadas,
    }

    return render(request, "core/dashboard_admin.html", contexto)


@solo_admin
def usuarios_lista(request):
    """Lista de todos los usuarios con filtros"""
    q = request.GET.get("q", "").strip()
    rol_seleccionado = request.GET.get("rol", "").strip()
    activo_seleccionado = request.GET.get("activo", "").strip()
    
    qs = User.objects.all().order_by("id")
    
    # Filtro por texto
    if q:
        qs = qs.filter(
            Q(username__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(email__icontains=q)
        )
    
    # Filtro por rol
    if rol_seleccionado:
        qs = qs.filter(groups__name=rol_seleccionado).distinct()
    
    # Filtro por estado activo
    if activo_seleccionado == "1":
        qs = qs.filter(is_active=True)
    elif activo_seleccionado == "0":
        qs = qs.filter(is_active=False)
    
    # Obtener todos los roles disponibles
    roles = Group.objects.values_list('name', flat=True).distinct()

    ctx = {
        "usuarios": qs,
        "q": q,
        "roles": roles,
        "rol_seleccionado": rol_seleccionado,
        "activo_seleccionado": activo_seleccionado,
    }

    return render(request, "core/usuarios_lista.html", ctx)


@login_required
@solo_admin
def usuario_crear(request):
    # =====================================================
    # ======== CREACIÓN MASIVA DE USUARIOS ================
    # =====================================================
    if request.method == "POST" and "crear_multiples" in request.POST:
        bulk_data = request.POST.get("bulk_users", "").strip()
        lines = bulk_data.split("\n")

        creados = 0
        errores = []

        for linea in lines:
            if not linea.strip():
                continue
            try:
                # Formato esperado: Nombre,Apellido,correo,Rol
                nombre, apellido, correo, rol = [x.strip() for x in linea.split(",")]

                # Generar username automáticamente a partir del correo
                username = correo.split("@")[0]

                # Evitar duplicados de usuario
                user = User.objects.filter(email=correo).first()
                if user:
                    errores.append(f"Usuario ya existe: {correo}")
                    continue

                # Crear usuario
                user = User.objects.create_user(
                    username=username,
                    password="Temp1234!",  # contraseña temporal
                    first_name=nombre,
                    last_name=apellido,
                    email=correo,
                    is_active=True
                )

                # Asignar grupo
                group, _ = Group.objects.get_or_create(name=rol)
                user.groups.add(group)

                # Crear profile solo si no existe
                Profile.objects.get_or_create(
                    user=user,
                    defaults={"cargo": rol, "group": group}
                )

                creados += 1

            except Exception as e:
                errores.append(f"Error en línea '{linea}': {e}")

        messages.success(request, f"Usuarios creados correctamente: {creados}")
        for err in errores:
            messages.error(request, err)

        return redirect("personas:usuarios_lista")

    # =====================================================
    # ======== CREACIÓN INDIVIDUAL (NORMAL) =============
    # =====================================================
    if request.method == "POST":
        form = UsuarioCrearForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Usuario '{user.username}' creado.")
            return redirect("personas:usuarios_lista")
    else:
        form = UsuarioCrearForm(initial={"is_active": True, "is_staff": False})

    return render(
        request, 
        "personas/usuario_form.html", 
        {"form": form, "modo": "crear"}
    )

@solo_admin
def usuario_editar(request, pk):
    """Editar un usuario existente"""
    from personas.forms import UsuarioEditarForm
    
    user = get_object_or_404(User, pk=pk)
    
    if request.method == "POST":
        form = UsuarioEditarForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Usuario '{user.username}' actualizado correctamente.")
            return redirect("core:usuarios_lista")
    else:
        form = UsuarioEditarForm(instance=user)
    
    return render(request, "core/usuario_form.html", {
        "form": form, 
        "modo": "editar", 
        "obj": user
    })


@solo_admin
def usuario_detalle(request, pk):
    """Ver detalles de un usuario"""
    user = get_object_or_404(User, pk=pk)
    groups = list(user.groups.values_list("name", flat=True))
    
    return render(request, "core/usuario_detalle.html", {
        "obj": user, 
        "groups": groups
    })


@solo_admin
@require_POST
def usuario_toggle_activo(request, pk):
    """Activar/Desactivar un usuario"""
    user = get_object_or_404(User, pk=pk)

    # Prevenir que el usuario se desactive a sí mismo
    if user == request.user and user.is_active:
        messages.warning(request, "No puedes desactivar tu propio usuario mientras estás conectado.")
        return redirect("core:usuarios_lista")

    # Cambiar estado
    user.is_active = not user.is_active
    user.save(update_fields=["is_active"])

    estado = "activado" if user.is_active else "desactivado"
    messages.success(request, f"Usuario '{user.username}' {estado} correctamente.")
    
    return redirect("core:usuarios_lista")