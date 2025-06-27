from django.shortcuts import render, redirect
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import timedelta
from django.http import JsonResponse
from django.template.loader import render_to_string
from tareas.models import (
    Pacientes, 
    Fichaclinico, 
    Personal,
    Consultas,
    Hospitalizaciones
)

def validar_doctor(request):
    """Valida si el usuario está logueado y es de rol 'Doctor'"""
    return (request.session.get('usuario_id') and 
            request.session.get('rol') == 'Doctor')

def menu_doctor(request):
    """Vista principal del panel del doctor"""
    if not validar_doctor(request):
        return redirect('login')

    # Obtener datos del doctor desde sesión
    personal_id = request.session.get('usuario_id')
    nombre_completo = request.session.get('nombre', 'Doctor/a')
    
    # Obtener estadísticas recientes
    ahora = timezone.now()
    hace_24_horas = ahora - timedelta(hours=24)
    
    fichas_24h = Fichaclinico.objects.filter(
        personalid=personal_id,
        fechaapertura__gte=hace_24_horas
    )
    
    consultas_recientes = Consultas.objects.filter(
        personalid=personal_id,
        fechaconsulta__gte=hace_24_horas
    ).count()
    
    pacientes_hospitalizados = Hospitalizaciones.objects.filter(
        personalid=personal_id,
        estado=True
    ).count()

    return render(request, 'doctor/MenuDoctor.html', {
        'nombre_completo': nombre_completo,
        'fichas': fichas_24h,
        'total_consultas': consultas_recientes,
        'total_hospitalizados': pacientes_hospitalizados
    })

def ver_pacientes(request):
    if not validar_doctor(request):
        return redirect('login')

    try:
        search_query = request.GET.get('q', '').strip()
        search_by = request.GET.get('search-by', 'apellido')

        pacientes_list = Pacientes.objects.all()

        # Filtrado según criterio y texto de búsqueda
        if search_query:
            if search_by == 'apellido':
                pacientes_list = pacientes_list.filter(apellidos__icontains=search_query)
            elif search_by == 'nombre':
                pacientes_list = pacientes_list.filter(nombres__icontains=search_query)
            elif search_by == 'cedula':
                pacientes_list = pacientes_list.filter(numerodocumento__icontains=search_query)

        # Ordenar del más reciente al más antiguo (suponiendo pacienteid autoincremental)
        pacientes_list = pacientes_list.order_by('-pacienteid')

        # Paginación: 10 pacientes por página
        paginator = Paginator(pacientes_list, 10)
        page_number = request.GET.get('page')
        pacientes = paginator.get_page(page_number)

        return render(request, 'doctor/PacienteDoctor/PacienteDoctor.html', {
            'pacientes': pacientes,
            'total_pacientes': pacientes_list.count(),
            'search_query': search_query,
            'search_by': search_by,
        })

    except Exception as e:
        print(f"Error al obtener pacientes: {e}")
        return redirect('menu_doctor')
    
# Vista de perfil del doctor (ejemplo adicional)
# Vista de perfil del doctor
def perfil_doctor(request):
    """Muestra el perfil del doctor actual con estadísticas y últimas consultas"""
    if not validar_doctor(request):
        return redirect('login')
    
    try:
        # Obtener ID del doctor desde sesión
        personal_id = request.session.get('usuario_id')
        
        # Buscar al doctor autenticado
        doctor = Personal.objects.get(
            personalid=personal_id,
            rol='Doctor'  # Filtrar por rol
        )

        # Estadísticas del doctor
        total_pacientes = Consultas.objects.filter(
            personalid=personal_id
        ).values('pacienteid').distinct().count()

        total_consultas = Consultas.objects.filter(
            personalid=personal_id
        ).count()

        # Obtener las últimas 5 consultas
        ultimas_consultas = Consultas.objects.filter(
            personalid=personal_id
        ).select_related('pacienteid').order_by('-fechaconsulta')[:5]

        return render(request, 'doctor/PerfilDoctor.html', {
            'doctor': doctor,
            'total_pacientes': total_pacientes,
            'total_consultas': total_consultas,
            'especialidad': doctor.especialidadid,
            'ultimas_consultas': ultimas_consultas
        })

    except Personal.DoesNotExist:
        return redirect('menu_doctor')

# Ver hospitalizaciones desde el módulo doctor
def ver_hospitalizaciones(request):
    """Muestra las hospitalizaciones activas del doctor"""
    if not validar_doctor(request):
        return redirect('login')
    
    try:
        personal_id = request.session.get('usuario_id')
        hospitalizaciones = Hospitalizaciones.objects.filter(
            personalid=personal_id,
            estado=True  # Solo hospitalizaciones activas
        ).select_related(
            'pacienteid',
            'habitacionid'
        ).order_by('-fechaingreso')
        
        return render(request, 'doctor/ver_hospitalizaciones.html', {
            'hospitalizaciones': hospitalizaciones,
            'total_hospitalizados': hospitalizaciones.count()
        })
        
    except Exception as e:
        print(f"Error al obtener hospitalizaciones: {str(e)}")
        return redirect('menu_doctor')

# Vista para consultar un paciente específico
def consulta_paciente(request, id):
    """Muestra detalles de un paciente para consulta"""
    if not validar_doctor(request):
        return redirect('login')
    
    try:
        personal_id = request.session.get('usuario_id')
        paciente = Pacientes.objects.get(pacienteid=id)
        
        # Verificar que el doctor tenga relación con el paciente
        if not Consultas.objects.filter(
            pacienteid=id,
            personalid=personal_id
        ).exists():
            return redirect('ver_pacientes')
        
        # Obtener consultas anteriores con este doctor
        consultas = Consultas.objects.filter(
            pacienteid=id,
            personalid=personal_id
        ).order_by('-fechaconsulta')[:5]
        
        return render(request, 'doctor/consulta.html', {
            'paciente': paciente,
            'consultas_anteriores': consultas
        })
        
    except Pacientes.DoesNotExist:
        return redirect('ver_pacientes')

# Vista para ver historial del paciente
def historial_paciente(request, id):
    """Muestra el historial completo del paciente"""
    if not validar_doctor(request):
        return redirect('login')
    
    try:
        personal_id = request.session.get('usuario_id')
        paciente = Pacientes.objects.get(pacienteid=id)
        
        # Verificar relación doctor-paciente
        if not Consultas.objects.filter(
            pacienteid=id,
            personalid=personal_id
        ).exists():
            return redirect('ver_pacientes')
        
        # Obtener todos los registros médicos
        consultas = Consultas.objects.filter(
            pacienteid=id
        ).order_by('-fechaconsulta')
        
        hospitalizaciones = Hospitalizaciones.objects.filter(
            pacienteid=id
        ).order_by('-fechaingreso')
        
        fichas = Fichaclinico.objects.filter(
            pacienteid=id
        ).order_by('-fechaapertura')
        
        return render(request, 'doctor/historial.html', {
            'paciente': paciente,
            'consultas': consultas,
            'hospitalizaciones': hospitalizaciones,
            'fichas': fichas
        })
        
    except Pacientes.DoesNotExist:
        return redirect('ver_pacientes')

# Vista para cerrar sesión
def logout_view(request):
    """Cierra la sesión del usuario"""
    request.session.flush()
    return redirect('login')

# Vista para manejar las fichas clínicas del doctor
def ficha_clinico_doctor(request):
    """Gestiona la creación y visualización de fichas clínicas"""
    if not validar_doctor(request):
        return redirect('login')
    
    personal_id = request.session.get('usuario_id')
    
    if request.method == 'POST':
        try:
            paciente_id = request.POST.get('paciente_id')
            motivo = request.POST.get('motivo')
            tipo = request.POST.get('tipo')
            
            paciente = Pacientes.objects.get(pacienteid=paciente_id)
            personal = Personal.objects.get(personal_id=personal_id)
            
            ficha = Fichaclinico(
                pacienteid=paciente,
                personalid=personal,
                fechaapertura=timezone.now(),
                motivoconsulta=motivo,
                tipoatencion=tipo,
                estado="Activa",
            )
            ficha.save()
            
            # Devolver respuesta JSON para AJAX
            fichas_24h = Fichaclinico.objects.filter(
                personalid=personal_id,
                fechaapertura__gte=timezone.now()-timedelta(hours=24)
            )
            html = render_to_string('doctor/tabla_fichas.html', {'fichas': fichas_24h})
            return JsonResponse({'status': 'success', 'html': html})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    # GET request: Mostrar fichas recientes
    fichas_24h = Fichaclinico.objects.filter(
        personalid=personal_id,
        fechaapertura__gte=timezone.now()-timedelta(hours=24)
    ).select_related('pacienteid')
    
    return render(request, 'doctor/ficha_clinico_doctor.html', {
        'fichas': fichas_24h,
        'pacientes': Pacientes.objects.all()  # Para el select de pacientes
    })