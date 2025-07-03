from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import datetime
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import timedelta
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.template.loader import render_to_string
from tareas.models import (
    Pacientes, 
    Fichaclinico, 
    Personal,
    Consultas,
    Hospitalizaciones,
    Consultaservicios, 
    Servicios,
    Habitaciones,
    Tiposhabitacion,
    Hospitalizacionservicios,
    Tiposalta
)

def validar_doctor(request):
    """Valida si el usuario está logueado y es de rol 'Doctor'"""
    return (request.session.get('usuario_id') and 
            request.session.get('rol') == 'Doctor')

from tareas.models import Fichaclinico

def menu_doctor(request):
    if not validar_doctor(request):
        return redirect('login')

    personal_id = request.session.get('usuario_id')
    nombre_completo = request.session.get('nombre', 'Doctor/a')

    ahora = timezone.now()
    hace_24_horas = ahora - timedelta(hours=24)

    consultas_recientes = Consultas.objects.filter(
        personalid=personal_id,
        fechaconsulta__gte=hace_24_horas
    ).count()

    pacientes_hospitalizados = Hospitalizaciones.objects.filter(
        personalid=personal_id,
        estado=True
    ).count()

    # ✅ Traer todas las fichas clínicas creadas en las últimas 24 horas
    fichas = Fichaclinico.objects.filter(
        fechaapertura__gte=hace_24_horas
    ).select_related('pacienteid')

    return render(request, 'doctor/MenuDoctor.html', {
        'nombre_completo': nombre_completo,
        'total_consultas': consultas_recientes,
        'total_hospitalizados': pacientes_hospitalizados,
        'fichas': fichas,  # 👈 Añadimos al contexto
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
    
# esta es la funcion de PerfilPacienteDoctor
def perfil_paciente_doctor(request, pacienteid):
    """Muestra el perfil completo del paciente y sus fichas clínicas recientes"""
    if not validar_doctor(request):
        return redirect('login')

    try:
        paciente = get_object_or_404(Pacientes, pacienteid=pacienteid)

        # Filtrar fichas clínicas de las últimas 24 horas del mismo paciente
        hace_24h = timezone.now() - timedelta(hours=24)
        fichas_recientes = Fichaclinico.objects.filter(
            pacienteid=paciente,
            fechaapertura__gte=hace_24h
        ).order_by('-fechaapertura')

        # No necesitas desglosar campos aquí, el template puede acceder directamente a:
        # paciente.contactoemergencia, paciente.enfermedadesbase, paciente.idioma, etc.

        return render(request, 'doctor/PacienteDoctor/PerfilPacienteDoctor.html', {
            'paciente': paciente,
            'fichas_recientes': fichas_recientes
        })

    except Exception as e:
        print(f"[Error] perfil_paciente_doctor: {e}")
        return redirect('ver_pacientes')
    

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
        ).select_related('pacienteid', 'habitacionid', 'habitacionid__tipohabitacionid')

        print("✅ Renderizando plantilla Hospitalizaciones.html")

        return render(request, 'doctor/Hospitalizaciones.html', {
            'hospitalizaciones': hospitalizaciones,
            'total_hospitalizados': hospitalizaciones.count()
        })

    except Exception as e:
        print(f"Error al obtener hospitalizaciones: {str(e)}")
        return redirect('menu_doctor')

#servicios de hospitalizacion

def servicios_hospitalizacion(request, hosp_id):
    try:
        # Obtener la hospitalización usando el id
        hospitalizacion = Hospitalizaciones.objects.get(hospitalizacionid=hosp_id)

        # Obtener el personal que solicitó la hospitalización
        personal_solicitante = hospitalizacion.personalid

        # Si el formulario ha sido enviado
        if request.method == 'POST':
            # Obtener los servicios seleccionados y otros datos
            servicios_seleccionados = request.POST.getlist('servicios')
            
            for servicio_id in servicios_seleccionados:
                # Obtener el servicio
                servicio = Servicios.objects.get(servicioid=servicio_id)
                
                # Obtener cantidad y observación (si existen)
                cantidad = int(request.POST.get(f'cantidad_{servicio_id}', 1))  # Definir cantidad por defecto como 1
                observaciones = request.POST.get(f'observacion_{servicio_id}', '')

                # Crear una nueva entrada en la tabla Hospitalizacionservicios
                Hospitalizacionservicios.objects.create(
                    hospitalizacionid=hospitalizacion,
                    servicioid=servicio,
                    cantidad=cantidad,
                    fechaservicio=timezone.now(),
                    observaciones=observaciones,
                    personalsolicitanteid=personal_solicitante,  # Personal solicitante
                    fecharegistro=timezone.now(),
                    estado=True,  # O el estado que desees
                    facturado=False  # O lo que corresponda
                )

            # Redirigir a la misma página o a otra página después de guardar
            return redirect('servicios_hospitalizacion', hosp_id=hosp_id)

        # Si el formulario no ha sido enviado, simplemente renderiza los servicios registrados
        servicios_hospitalizacion = Hospitalizacionservicios.objects.filter(hospitalizacionid=hospitalizacion)

        return render(request, 'doctor/ServiciosHospitalizacion.html', {
            'hospitalizacion': hospitalizacion,
            'servicios_hospitalizacion': servicios_hospitalizacion,
            'personal_solicitante': personal_solicitante,
            'servicios_disponibles': Servicios.objects.all(),  # Los servicios disponibles
        })

    except Hospitalizaciones.DoesNotExist:
        return redirect('ver_hospitalizaciones')
#
# alta doctor
#     
def alta_doctor(request, hosp_id):
    hospitalizacion = get_object_or_404(Hospitalizaciones, hospitalizacionid=hosp_id)

    if request.method == 'POST':
        tipoaltaid = request.POST.get('tipoaltaid')  # Obtener el tipo de alta
        fechaalta = request.POST.get('fechaalta')
        diagnostico = request.POST.get('diagnostico')
        tratamientoaplicado = request.POST.get('tratamientoaplicado')
        observaciones = request.POST.get('observaciones')  # Obtener las observaciones

        # Verificar si se llenan los campos de diagnóstico y tratamiento
        if not diagnostico:
            diagnostico = ''
        if not tratamientoaplicado:
            tratamientoaplicado = ''
        if not observaciones:
            observaciones = ''  # Asegurarse de que las observaciones no queden vacías

        # Convertir la fecha de alta a la zona horaria adecuada
        fechaalta = timezone.make_aware(timezone.datetime.strptime(fechaalta, "%Y-%m-%d"), timezone.get_current_timezone())

        # Actualizar la hospitalización
        hospitalizacion.tipoaltaid_id = tipoaltaid
        hospitalizacion.fechaalta = fechaalta
        hospitalizacion.diagnostico = diagnostico
        hospitalizacion.tratamientoaplicado = tratamientoaplicado
        hospitalizacion.observaciones = observaciones  # Asignar las observaciones

        hospitalizacion.save()  # Guardar los cambios

        return redirect('ver_hospitalizaciones')  # Redirigir a la vista de hospitalizaciones

    return render(request, 'doctor/AltaDoctor.html', {
        'hospitalizacion': hospitalizacion,
        'tiposalta': Tiposalta.objects.all(),  # Pasar los tipos de alta para el formulario
    })
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
            motivo = request.POST.get('motivo', '').strip()
            tipo = request.POST.get('tipo', '').strip()

            paciente = get_object_or_404(Pacientes, pacienteid=paciente_id)
            personal = get_object_or_404(Personal, personalid=personal_id)

            ficha = Fichaclinico.objects.create(
                pacienteid=paciente,
                personalid=personal,
                fechaapertura=timezone.now(),
                motivoconsulta=motivo,
                tipoatencion=tipo,
                estado="Activa",
            )

            fichas_24h = Fichaclinico.objects.filter(
                personalid=personal,
                fechaapertura__gte=timezone.now() - timedelta(hours=24)
            ).select_related('pacienteid')

            html = render_to_string('doctor/tabla_fichas.html', {'fichas': fichas_24h})
            return JsonResponse({'status': 'success', 'html': html})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    # GET: Mostrar fichas creadas en las últimas 24 horas
    fichas_24h = Fichaclinico.objects.filter(
        personalid=personal_id,
        fechaapertura__gte=timezone.now() - timedelta(hours=24)
    ).select_related('pacienteid')

    return render(request, 'doctor/ficha_clinico_doctor.html', {
        'fichas': fichas_24h,
        'pacientes': Pacientes.objects.all()  # Para select en formulario
    })

#funcion de perfil del paciente para el modulo de doctor
def crear_consulta_doctor(request, pacienteid):
    if not validar_doctor(request):
        return redirect('login')

    paciente = get_object_or_404(Pacientes, pacienteid=pacienteid)
    personal_id = request.session.get('usuario_id')

    ficha_reciente = (
        Fichaclinico.objects
        .filter(
            pacienteid=paciente,
            fechaapertura__gte=timezone.now() - timedelta(hours=24)
        )
        .order_by('-fechaapertura')
        .select_related('personalid')
        .first()
    )

    servicios = Servicios.objects.filter(estado=True)
    tipos_habitacion = Tiposhabitacion.objects.all()
    habitaciones_disponibles = Habitaciones.objects.filter(estado=True, disponible=True)

    if request.method == 'POST':
        motivocita = request.POST.get('motivocita', '').strip()
        diagnostico = request.POST.get('diagnostico', '').strip()
        tratamiento = request.POST.get('tratamiento', '').strip()
        observaciones = request.POST.get('observaciones', '').strip()
        estado = request.POST.get('estado', 'True') == 'True'
        costo = request.POST.get('costo')

        requiere_servicio = request.POST.get('requiere_servicio') == 'on'
        servicio_id = request.POST.get('servicioid')
        cantidad = request.POST.get('cantidad')
        observacion_servicio = request.POST.get('observaciones_servicio', '').strip()

        requiere_hospitalizacion = request.POST.get('requiere_hospitalizacion') == 'on'
        tipo_habitacion_id = request.POST.get('tipo_habitacion')
        habitacion_id = request.POST.get('habitacionid')
        motivo_hosp = request.POST.get('motivohospitalizacion', '').strip()

        if motivocita and diagnostico and tratamiento:
            consulta = Consultas.objects.create(
                pacienteid=paciente,
                personalid_id=personal_id,
                fechaconsulta=timezone.now(),
                motivocita=motivocita,
                diagnostico=diagnostico,
                tratamiento=tratamiento,
                observaciones=observaciones,
                estado=estado,
                costo=costo
            )

            if requiere_servicio and servicio_id and cantidad:
                Consultaservicios.objects.create(
                    consultaid=consulta,
                    servicioid_id=servicio_id,
                    cantidad=int(cantidad),
                    fechaservicio=timezone.now(),
                    observaciones=observacion_servicio,
                    fecharegistro=timezone.now(),
                    estado=True,
                    facturado=False
                )

            if requiere_hospitalizacion and habitacion_id and motivo_hosp:
                Hospitalizaciones.objects.create(
                    pacienteid=paciente,
                    personalid_id=personal_id,
                    habitacionid_id=habitacion_id,
                    fechaingreso=timezone.now(),
                    motivohospitalizacion=motivo_hosp,
                    fecharegistro=timezone.now(),
                    estado=True,
                    facturado=False
                )

                # Marcar la habitación como ocupada
                Habitaciones.objects.filter(pk=habitacion_id).update(disponible=False)

            return redirect('perfil_paciente_doctor', pacienteid=pacienteid)

    return render(request, 'doctor/PacienteDoctor/ConsultaDoctor.html', {
        'paciente': paciente,
        'ficha_reciente': ficha_reciente,
        'servicios': servicios,
        'tipos_habitacion': tipos_habitacion,
        'habitaciones': habitaciones_disponibles,
    })

# habitaciones disponibles para los pacientes 
@require_GET
def habitaciones_disponibles(request, tipoid):
    habitaciones = Habitaciones.objects.filter(
        tipohabitacionid=tipoid,
        disponible=True,
        estado=True
    ).values('habitacionid', 'numero')

    data = {
        'habitaciones': [
            {
                'id': h['habitacionid'],
                'nombre': h['numero']
            } for h in habitaciones
        ]
    }
    return JsonResponse(data)

#actualizar posisiblemente lo eliminemos 

def actualizar_paciente_doctor(request, pacienteid):
    if not validar_doctor(request):
        return redirect('login')

    paciente = get_object_or_404(Pacientes, pacienteid=pacienteid)

    if request.method == 'POST':
        paciente.nombres = request.POST.get('nombres', paciente.nombres)
        paciente.apellidos = request.POST.get('apellidos', paciente.apellidos)
        paciente.numerodocumento = request.POST.get('numerodocumento', paciente.numerodocumento)
        paciente.telefono = request.POST.get('telefono', paciente.telefono)
        paciente.email = request.POST.get('email', paciente.email)
        paciente.direccion = request.POST.get('direccion', paciente.direccion)
        paciente.save()
        return redirect('perfil_paciente_doctor', pacienteid=pacienteid)

    return render(request, 'doctor/ActualizarPaciente.html', {'paciente': paciente})

def historial_paciente(request, pacienteid):
    # Obtener el paciente por ID o lanzar 404 si no existe
    paciente = get_object_or_404(Pacientes, pacienteid=pacienteid)

    # Obtener parámetros GET para el filtro de fechas
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    # Obtener fichas del paciente
    fichas = Fichaclinico.objects.filter(pacienteid=paciente)

    # Aplicar filtros de fecha si se reciben correctamente
    if fecha_inicio:
        try:
            fecha_inicio_obj = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fichas = fichas.filter(fechaapertura__date__gte=fecha_inicio_obj)
        except ValueError:
            fecha_inicio = None  # Si el formato es incorrecto, se ignora el filtro

    if fecha_fin:
        try:
            fecha_fin_obj = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            fichas = fichas.filter(fechaapertura__date__lte=fecha_fin_obj)
        except ValueError:
            fecha_fin = None  # Si el formato es incorrecto, se ignora el filtro

    # Preparar contexto para el template
    context = {
        'paciente': paciente,
        'fichas': fichas.order_by('-fechaapertura'),
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    }

    # Renderizar plantilla correspondiente al historial del doctor
    return render(request, 'doctor/PacienteDoctor/Historial_Doctor.html', context)
#
#historiral de los pacientes del doctor
#
def ver_historial_detalle_doctor(request, fichaid):
    """Muestra todos los detalles clínicos de una ficha específica (módulo Doctor)"""
    if not validar_doctor(request):
        return redirect('login')

    try:
        ficha = get_object_or_404(Fichaclinico, fichaid=fichaid)  # ✅ Campo corregido

        doctor_responsable = ficha.personalid if ficha.personalid.rol == 'Doctor' else None

        consultas = Consultas.objects.filter(
            pacienteid=ficha.pacienteid,
            fechaconsulta__gte=ficha.fechaapertura
        ).order_by('-fechaconsulta')

        hospitalizaciones = Hospitalizaciones.objects.filter(
            pacienteid=ficha.pacienteid,
            fechaingreso__gte=ficha.fechaapertura
        ).order_by('-fechaingreso')

        return render(request, 'doctor/PacienteDoctor/Ver_Historial_Doctor.html', {
            'ficha': ficha,
            'doctor_responsable': doctor_responsable,
            'consultas': consultas,
            'hospitalizaciones': hospitalizaciones
        })

    except Exception as e:
        print(f"[Error] ver_historial_detalle_doctor: {str(e)}")
        return redirect('menu_doctor')