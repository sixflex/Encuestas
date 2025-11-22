from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User, Group
from django.contrib.auth import logout
from registration.models import Profile
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.views.decorators.http import require_POST
from .forms import UsuarioCrearForm, UsuarioEditarForm
from .utils import solo_admin
from core.utils import solo_direccion, solo_cuadrilla, solo_territorial
from core.models import Incidencia, Departamento, Direccion
from registration.models import Profile

@login_required
def dashboard_admin(request):
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

    return render(request, "personas/dashboards/admin.html", contexto)

@login_required
@solo_territorial
def dashboard_territorial(request):
    # Obtener las últimas 10 incidencias para mostrar en el dashboard
    incidencias = Incidencia.objects.all().order_by('-creadoEl')[:10]
    return render(request, "personas/dashboards/territorial.html", {
        'incidencias': incidencias
    })


@solo_cuadrilla
def dashboard_jefe(request):
    """
    Dashboard para Jefe de Cuadrilla.
    Muestra las incidencias asignadas a su cuadrilla.
    """
    # Obtener el profile del usuario actual
    try:
        profile = request.user.profile
    except:
        profile = None
    
    # Buscar las cuadrillas donde el usuario es el encargado o el usuario asignado
    from core.models import JefeCuadrilla
    
    if profile:
        cuadrillas = JefeCuadrilla.objects.filter(
            Q(usuario=profile) | Q(encargado=profile)
        )
    else:
        cuadrillas = JefeCuadrilla.objects.none()
    
    # Obtener las incidencias asignadas a las cuadrillas del usuario
    incidencias_pendientes = []
    incidencias_en_progreso = []
    incidencias_Completadas = []
    
    if cuadrillas.exists():
        # Filtrar incidencias por las cuadrillas del usuario
        incidencias_pendientes = Incidencia.objects.filter(
            cuadrilla__in=cuadrillas,
            estado='Pendiente'
        ).order_by('-creadoEl')
        
        incidencias_en_progreso = Incidencia.objects.filter(
            cuadrilla__in=cuadrillas,
            estado='En Progreso'
        ).order_by('-creadoEl')
        
        incidencias_Completadas = Incidencia.objects.filter(
            cuadrilla__in=cuadrillas,
            estado__in=['Completada', 'Validada', 'Rechazada']
        ).order_by('-actualizadoEl')[:10]  # Últimas 10 Completadas
    
    return render(request, "personas/dashboards/jefeCuadrilla.html", {
        'cuadrillas': cuadrillas,
        'incidencias_pendientes': incidencias_pendientes,
        'incidencias_en_progreso': incidencias_en_progreso,
        'incidencias_Completadas': incidencias_Completadas,
    })
#----------------------------------------------------------------------
@login_required
@solo_direccion
def dashboard_direccion(request):
    return render(request, "personas/dashboards/direccion.html")

@login_required
def dashboard_departamento(request):
    """
    Dashboard para usuarios del grupo Departamento.
    Muestra incidencias pendientes para asignar a cuadrillas.
    """
    from core.models import Incidencia, JefeCuadrilla, Departamento
    from django.db.models import Q, Count
    
    roles = set(request.user.groups.values_list("name", flat=True))
    
    if not ("Departamento" in roles or request.user.is_superuser or "Administrador" in roles):
        messages.error(request, "No tienes acceso a este dashboard")
        return check_profile(request)
    
    # Obtener departamento del usuario
    try:
        departamento = Departamento.objects.get(encargado=request.user.profile)
    except:
        departamento = None
    
    # Incidencias del departamento
    if departamento:
        incidencias_pendientes = Incidencia.objects.filter(
            departamento=departamento,
            estado='Pendiente'
        ).order_by('-creadoEl')
        
        incidencias_en_progreso = Incidencia.objects.filter(
            departamento=departamento,
            estado='En progreso'
        ).order_by('-creadoEl')
        
        incidencias_Completadas = Incidencia.objects.filter(
            departamento=departamento,
            estado='Completada'
        ).order_by('-creadoEl')
        
        # Cuadrillas del departamento
        cuadrillas = JefeCuadrilla.objects.filter(departamento=departamento)
    else:
        # Si es admin, ver todas
        incidencias_pendientes = Incidencia.objects.filter(estado='Pendiente').order_by('-creadoEl')
        incidencias_en_progreso = Incidencia.objects.filter(estado='En Progreso').order_by('-creadoEl')
        incidencias_Completadas = Incidencia.objects.filter(estado='Completada').order_by('-creadoEl')
        cuadrillas = JefeCuadrilla.objects.all()
    
    ctx = {
        'departamento': departamento,
        'incidencias_pendientes': incidencias_pendientes,
        'incidencias_en_progreso': incidencias_en_progreso,
        'incidencias_Completadas': incidencias_Completadas,
        'cuadrillas': cuadrillas,
        'total_pendientes': incidencias_pendientes.count(),
        'total_en_progreso': incidencias_en_progreso.count(),
        'total_Completadas': incidencias_Completadas.count(),
    }
    
    return render(request, 'personas/dashboards/departamento.html', ctx)
#--------------------------------------------------------------------

@login_required
def check_profile(request):
    """
    Redirige al usuario al dashboard correspondiente según su rol.
    """
    user = request.user
    
    # Si es superusuario, va directo al admin
    if user.is_superuser:
        return redirect("personas:dashboard_admin")
    
    grupos = list(user.groups.values_list("name", flat=True))

    try:
        profile = Profile.objects.select_related('group').get(user=user)
    except Profile.DoesNotExist:
        messages.error(request, "No se encontró un perfil asociado a este usuario.")
        logout(request)
        return redirect("login")

    # Obtener el nombre del grupo y limpiarlo
    if not profile.group:
        messages.error(request, "Tu usuario no tiene un grupo/rol asignado. Contacta al administrador.")
        logout(request)
        return redirect("login")
    
    rol = profile.group.name.strip()
    
    # Debug: puedes comentar esto después de probar
    print(f"Usuario: {user.username}, Rol: '{rol}'")
    
    # Redirección según el rol
    if "Administrador" in grupos:
        return redirect("personas:dashboard_admin")
    elif "Territorial" in grupos:
        return redirect("personas:dashboard_territorial")
    elif "Jefe de Cuadrilla" in grupos:
        return redirect("personas:dashboard_jefeCuadrilla")
    elif "Dirección"in grupos:
        return redirect("personas:dashboard_direccion")
    elif "Departamento"in grupos:
        return redirect("personas:dashboard_departamento")
    else:
        messages.error(request, f"Rol '{rol}' no reconocido. Contacta al administrador.")
        logout(request)
        return redirect("login")
    

@login_required
@solo_admin
def usuarios_lista(request):
    q = request.GET.get("q", "").strip()
    rol_seleccionado = request.GET.get("rol", "").strip()
    qs = User.objects.all().order_by("id")
    
    #filtro por texto
    if q:
        qs = qs.filter(
            Q(username__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(email__icontains=q)
        )
    #filtro por rol
    if rol_seleccionado:
        qs = qs.filter(profile_group__name=rol_seleccionado)
    
    roles = Profile.objects.values_list('group__name', flat=True).distinct()

    ctx = {
        "usuarios": qs,
        "q": q,
        "roles": roles,
        "rol_seleccionado": rol_seleccionado,
    }

    return render(request, "personas/usuarios_lista.html", ctx)

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
@login_required
@solo_admin
def usuario_editar(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        form = UsuarioEditarForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Usuario '{user.username}' actualizado.")
            return redirect("personas:usuarios_lista")
    else:
        form = UsuarioEditarForm(instance=user)
    return render(request, "personas/usuario_form.html", {"form": form, "modo": "editar", "obj": user})

@login_required
@solo_admin
@require_POST
def usuario_toggle_activo(request, pk):
    user = get_object_or_404(User, pk=pk)

    if user == request.user and user.is_active:
        messages.warning(request, "No puedes desactivar tu propio usuario mientras estás conectado.")
        return redirect("personas:usuarios_lista")

    user.is_active = not user.is_active
    user.save(update_fields=["is_active"])

    estado = "activado" if user.is_active else "desactivado"
    messages.success(request, f"Usuario '{user.username}' {estado}.")
    return redirect("personas:usuarios_lista")

@login_required
@solo_admin
def usuario_detalle(request, pk):
    user = get_object_or_404(User, pk=pk)
    groups = list(user.groups.values_list("name", flat=True))
    return render(request, "personas/usuario_detalle.html", {"obj": user, "groups": groups})

def cerrar_sesion(request):
    logout(request)
    request.session.flush()
    messages.info(request, "Sesión cerrada correctamente.")
    return redirect("/accounts/login/")