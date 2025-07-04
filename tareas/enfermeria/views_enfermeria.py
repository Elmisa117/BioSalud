import json
from django.db import connection,IntegrityError
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from datetime import datetime, date
from django.views.decorators.csrf import csrf_exempt


from tareas.models import (
    Pacientes,
    Personal,
    Especialidades,
    Fichaclinico,
    Consultas,
    Consultaservicios,
    Hospitalizaciones,
    Hospitalizacionservicios,
    Servicios
)

# ----------------------------
# MENÚ PRINCIPAL DE ENFERMERÍA
# ----------------------------
def menu_enfermeria_enfermeria(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    nombre = request.session.get('nombre', 'Usuario')  # <- ahora lee 'nombre'
    return render(request, 'enfermeria/MenuEnfermera.html', {'nombre': nombre})


# ----------------------------
# VISTA DE PACIENTES
# ----------------------------
def vista_pacientes_enfermeria(request): 
    if not request.session.get('usuario_id'):
        return redirect('login')

    nombre = request.session.get('nombre_completo', 'Usuario')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT pacienteid, nombres, apellidos, numerodocumento
            FROM pacientes
            WHERE estado = TRUE
            ORDER BY fecharegistro DESC
        """)
        resultados = cursor.fetchall()

    pacientes = [
        {
            'id': fila[0],
            'nombres': fila[1],
            'apellidos': fila[2],
            'numero_documento': fila[3]
        }
        for fila in resultados
    ]

    return render(request, 'enfermeria/Paciente/Paciente.html', {
        'nombre': nombre,
        'pacientes_json': json.dumps(pacientes)
    })


def perfil_paciente_enfermeria(request, paciente_id):
    if not request.session.get('usuario_id'):
        return redirect('login')

    # Query para obtener los detalles del paciente
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                pacienteid, nombres, apellidos, numerodocumento, tipodocumento,
                fechanacimiento, edad, genero, direccion, telefono, email,
                gruposanguineo, alergias, observaciones,
                nombre_contacto_emergencia, telefono_contacto_emergencia, parentesco_contacto_emergencia,
                enfermedades_base, idioma_principal
            FROM pacientes
            WHERE pacienteid = %s
        """, [paciente_id])
        fila = cursor.fetchone()

    if not fila:
        return render(request, 'enfermeria/Error.html', {'mensaje': 'Paciente no encontrado'})

    paciente = {
        'id': fila[0],
        'nombres': fila[1],
        'apellidos': fila[2],
        'numerodocumento': fila[3],
        'tipodocumento': fila[4],
        'fechanacimiento': fila[5].strftime('%Y-%m-%d') if fila[5] else '',
        'edad': fila[6],
        'genero': fila[7],
        'direccion': fila[8],
        'telefono': fila[9],
        'email': fila[10],
        'gruposanguineo': fila[11],
        'alergias': fila[12],
        'observaciones': fila[13],
        'nombre_contacto_emergencia': fila[14],
        'telefono_contacto_emergencia': fila[15],
        'parentesco_contacto_emergencia': fila[16],
        'enfermedades_base': fila[17],
        'idioma_principal': fila[18],
    }

    return render(request, 'enfermeria/Paciente/PerfilPaciente.html', {'paciente': paciente})

# ----------------------------
# REGISTRAR O EDITAR PACIENTE
# ----------------------------
@csrf_exempt
def registrar_paciente_enfermeria(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    paciente_id = request.GET.get('id')
    paciente_datos = {}

    if request.method == 'POST':
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

        paciente_id = request.POST.get('paciente_id')
        nombres = request.POST.get('nombres')
        apellidos = request.POST.get('apellidos')
        numero_documento = request.POST.get('numerodocumento')
        tipo_documento = request.POST.get('tipodocumento')
        fecha_nacimiento_str = request.POST.get('fechanacimiento') or None
        genero = request.POST.get('genero')
        direccion = request.POST.get('direccion')
        telefono = request.POST.get('telefono')
        email = request.POST.get('email')
        nombre_contacto_emergencia = request.POST.get('nombre_contacto_emergencia')
        telefono_contacto_emergencia = request.POST.get('telefono_contacto_emergencia')
        parentesco_contacto_emergencia = request.POST.get('parentesco_contacto_emergencia')
        grupo_sanguineo = request.POST.get('gruposanguineo')
        alergias = request.POST.get('alergias')
        observaciones = request.POST.get('observaciones')
        enfermedades_base = request.POST.get('enfermedades_base')
        idioma_principal = request.POST.get('idioma_principal')

        # Nuevos campos
        nombre_contacto = request.POST.get('nombre_contacto_emergencia')
        telefono_contacto = request.POST.get('telefono_contacto_emergencia')
        parentesco_contacto = request.POST.get('parentesco_contacto_emergencia')
        enfermedades_base = request.POST.get('enfermedades_base')
        idioma_principal = request.POST.get('idioma_principal')

        # Validación de fecha
        if fecha_nacimiento_str:
            fecha_nacimiento = datetime.strptime(fecha_nacimiento_str, "%Y-%m-%d").date()
            hoy = date.today()
            edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
        else:
            fecha_nacimiento = None
            edad = None
            messages.error(request, "Debe ingresar la fecha de nacimiento.")
            return render(request, 'enfermeria/Paciente/RegistrarPaciente/RegistrarPaciente.html', {
                "paciente": request.POST,
                "error": "Debe ingresar la fecha de nacimiento."
            })

        # Verificar duplicado
        if not paciente_id:
            with connection.cursor() as cursor:
                cursor.execute(""" 
                    SELECT COUNT(*) FROM pacientes 
                    WHERE numerodocumento = %s AND tipodocumento = %s 
                """, [numero_documento, tipo_documento])
                if cursor.fetchone()[0] > 0:
                    if is_ajax:
                        return JsonResponse({"mensaje": "duplicado"})
                    else:
                        messages.error(request, "El número de documento ya está registrado.")
                        return render(request, 'enfermeria/Paciente/RegistrarPaciente/RegistrarPaciente.html', {
                            "paciente": request.POST
                        })

        # Guardar paciente y obtener el ID en PostgreSQL
        with connection.cursor() as cursor:
            if paciente_id:
                cursor.execute(""" 
                    UPDATE pacientes SET
                        nombres = %s, apellidos = %s, numerodocumento = %s, tipodocumento = %s,
                        fechanacimiento = %s, edad = %s, genero = %s, direccion = %s,
                        telefono = %s, email = %s, gruposanguineo = %s, alergias = %s, observaciones = %s,
                        nombre_contacto_emergencia = %s, telefono_contacto_emergencia = %s,
                        parentesco_contacto_emergencia = %s, enfermedades_base = %s, idioma_principal = %s
                    WHERE pacienteid = %s
                """, [
                    nombres, apellidos, numero_documento, tipo_documento,
                    fecha_nacimiento, edad, genero, direccion,
                    telefono, email, grupo_sanguineo, alergias, observaciones,
                    nombre_contacto, telefono_contacto, parentesco_contacto,
                    enfermedades_base, idioma_principal, paciente_id
                ])
            else:
                cursor.execute(""" 
                    INSERT INTO pacientes (
                        nombres, apellidos, numerodocumento, tipodocumento,
                        fechanacimiento, edad, genero, direccion, telefono,
                        email, gruposanguineo, alergias, observaciones,
                        nombre_contacto_emergencia, telefono_contacto_emergencia,
                        parentesco_contacto_emergencia, enfermedades_base, idioma_principal,
                        fecharegistro, estado
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, TRUE)
                    RETURNING pacienteid;
                """, [
                    nombres, apellidos, numero_documento, tipo_documento,
                    fecha_nacimiento, edad, genero, direccion,
                    telefono, email, grupo_sanguineo, alergias, observaciones,
                    nombre_contacto, telefono_contacto, parentesco_contacto,
                    enfermedades_base, idioma_principal
                ])
                paciente_id = cursor.fetchone()[0]  # Captura el ID del paciente recién insertado

        # Mostrar el mensaje de éxito con el ID del paciente
        messages.success(request, f"Paciente guardado exitosamente. ID: {paciente_id}")
        
        # Renderiza la misma página sin redirigir, mostrando el mensaje de éxito
        return render(request, 'enfermeria/Paciente/RegistrarPaciente/RegistrarPaciente.html', {
            'paciente': request.POST  # Mantener los datos del formulario para que se muestren de nuevo
        })

    # Carga si es edición
    if paciente_id:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT nombres, apellidos, numerodocumento, tipodocumento,
                       fechanacimiento, edad, genero, direccion, telefono,
                       email, gruposanguineo, alergias, observaciones,
                       nombre_contacto_emergencia, telefono_contacto_emergencia,
                       parentesco_contacto_emergencia, enfermedades_base, idioma_principal
                FROM pacientes
                WHERE pacienteid = %s
            """, [paciente_id])
            fila = cursor.fetchone()
            if fila:
                paciente_datos = {
                    'id': paciente_id,
                    'nombres': fila[0],
                    'apellidos': fila[1],
                    'numerodocumento': fila[2],
                    'tipodocumento': fila[3],
                    'fechanacimiento': fila[4].strftime('%Y-%m-%d') if fila[4] else '',
                    'edad': fila[5],
                    'genero': fila[6],
                    'direccion': fila[7],
                    'telefono': fila[8],
                    'email': fila[9],
                    'gruposanguineo': fila[10],
                    'alergias': fila[11],
                    'observaciones': fila[12],
                    'nombre_contacto_emergencia': fila[13],
                    'telefono_contacto_emergencia': fila[14],
                    'parentesco_contacto_emergencia': fila[15],
                    'enfermedades_base': fila[16],
                    'idioma_principal': fila[17],
                }

    return render(request, 'enfermeria/Paciente/RegistrarPaciente/RegistrarPaciente.html', {
        'paciente': paciente_datos
    })
# ----------------------------
# REGISTRAR FICHA CLÍNICA
# ----------------------------
def ficha_clinico_enfermeria(request, id):
    # Obtener el paciente y los doctores
    paciente = get_object_or_404(Pacientes, pacienteid=id)
    doctores = Personal.objects.filter(rol='Doctor', estado=True).select_related('especialidadid')

    # Obtener el usuario autenticado (enfermera)
    enfermera_id = request.session.get('usuario_id')  # Esto asume que ya tienes el id del usuario (enfermera)
    enfermera = get_object_or_404(Personal, personalid=enfermera_id)

    if request.method == 'POST':
        # Capturar los datos del formulario
        personal_id = request.POST.get('personal_id')
        motivo = request.POST.get('motivo')
        diagnostico = request.POST.get('diagnostico')
        antecedentes_personales = request.POST.get('antecedentes_personales')
        antecedentes_familiares = request.POST.get('antecedentes_familiares')
        tipoatencion = request.POST.get('tipoatencion')

        # Capturar los signos vitales
        signos_vitales = {
            'ta': request.POST.get('ta'),
            'fc': request.POST.get('fc'),
            'fr': request.POST.get('fr'),
            'temp': request.POST.get('temp'),
            'spo2': request.POST.get('spo2')
        }

        # Otros campos
        tratamiento = request.POST.get('tratamiento')
        observaciones = request.POST.get('observaciones')

        errores = []

        # Validación de signos vitales
        try:
            fc = int(signos_vitales['fc'])
            if not (40 <= fc <= 180):
                errores.append("La frecuencia cardíaca (FC) debe estar entre 40 y 180.")
        except ValueError:
            errores.append("La frecuencia cardíaca (FC) debe ser un número válido.")

        try:
            fr = int(signos_vitales['fr'])
            if not (8 <= fr <= 40):
                errores.append("La frecuencia respiratoria (FR) debe estar entre 8 y 40.")
        except ValueError:
            errores.append("La frecuencia respiratoria (FR) debe ser un número válido.")

        try:
            temp = float(signos_vitales['temp'])
            if not (34.0 <= temp <= 42.0):
                errores.append("La temperatura debe estar entre 34.0°C y 42.0°C.")
        except ValueError:
            errores.append("La temperatura debe ser un número válido.")

        try:
            spo2 = int(signos_vitales['spo2'])
            if not (70 <= spo2 <= 100):
                errores.append("La saturación de oxígeno (SpO₂) debe estar entre 70% y 100%.")
        except ValueError:
            errores.append("La saturación de oxígeno debe ser un número válido.")

        # Validación de campos obligatorios
        if not personal_id:
            errores.append("Debe seleccionar un doctor.")
        if not motivo:
            errores.append("Debe ingresar el motivo de la consulta.")
        if not tipoatencion:
            errores.append("Debe seleccionar el tipo de atención.")

        # Si hay errores, mostrar los mensajes y volver al formulario
        if errores:
            for e in errores:
                messages.error(request, e)
            return render(request, 'enfermeria/Paciente/FichaClinico/FichaClinico.html', {
                'paciente': paciente,
                'doctores': doctores,
                'valores': request.POST
            })

        # Si no hay errores, guardar la ficha clínica
        ficha = Fichaclinico(
            pacienteid=paciente,
            personalid_id=personal_id,
            fechaapertura=timezone.now(),
            motivoconsulta=motivo,
            diagnosticoinicial=diagnostico,
            antecedentespersonales=antecedentes_personales,
            antecedentesfamiliares=antecedentes_familiares,
            signosvitales=signos_vitales,
            tratamientosugerido=tratamiento,
            observaciones=observaciones,
            estado="Activa",
            tipoatencion=tipoatencion,
            personalid=enfermera
        )
        ficha.save()

        # Mostrar mensaje de éxito y mantener en la misma página
        messages.success(request, "Ficha clínica guardada exitosamente.")
        return render(request, 'enfermeria/Paciente/FichaClinico/FichaClinico.html', {
            'paciente': paciente,
            'doctores': doctores
        })

    # Si el método es GET, mostramos el formulario
    return render(request, 'enfermeria/Paciente/FichaClinico/FichaClinico.html', {
        'paciente': paciente,
        'doctores': doctores
    })

# ----------------------------
# HISTORIAL CLÍNICO DEL PACIENTE
# ----------------------------
def historial_enfermeria(request, id):
    # Obtener el paciente desde la base de datos
    paciente = get_object_or_404(Pacientes, pacienteid=id)
    
    # Obtener los parámetros de fechas (si existen) de la URL
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    # Filtrar las fichas clínicas por el paciente
    fichas = Fichaclinico.objects.filter(pacienteid=paciente)

    # Si hay filtros de fecha, aplicar los filtros
    if fecha_inicio:
        fichas = fichas.filter(fechaapertura__date__gte=fecha_inicio)
    if fecha_fin:
        fichas = fichas.filter(fechaapertura__date__lte=fecha_fin)

    # Ordenar las fichas por la fecha de apertura de forma descendente
    fichas = fichas.order_by('-fechaapertura')

    # Si no se encontraron fichas en el rango de fechas
    if not fichas:
        messages.info(request, "No se encontraron fichas clínicas en este rango de fechas.")

    # Renderizar la plantilla con el contexto necesario
    return render(request, 'enfermeria/Paciente/Historial/Historial.html', {
        'paciente': paciente,
        'fichas': fichas,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin
    })
# ----------------------------
# VER DETALLE DE UNA FICHA CLÍNICA
# ----------------------------
def ver_historial_enfermeria(request, fichaid):
    # Obtener la ficha clínica
    ficha = get_object_or_404(Fichaclinico, fichaid=fichaid)
    
    # Deserializar los signos vitales de la ficha (si existen)
    signos_dict = ficha.signosvitales if ficha.signosvitales else {}
    
    # Inicializar variables
    enfermera_responsable = None
    doctor_responsable = None
    
    # Verificar el rol del personal de la ficha actual
    if ficha.personalid.rol == 'Enfermería':
        enfermera_responsable = ficha.personalid
    elif ficha.personalid.rol == 'Doctor':
        doctor_responsable = ficha.personalid
    
    # Si necesitas buscar el otro tipo de personal, puedes hacerlo así:
    # Si ya tienes una enfermera, buscar doctor
    if enfermera_responsable and not doctor_responsable:
        doctor_responsable = Personal.objects.filter(
            rol='Doctor',
            # Puedes agregar más filtros aquí si necesitas un doctor específico
        ).first()
    
    # Si ya tienes un doctor, buscar enfermera
    elif doctor_responsable and not enfermera_responsable:
        enfermera_responsable = Personal.objects.filter(
            rol='Enfermería',
            # Puedes agregar más filtros aquí si necesitas una enfermera específica
        ).first()
    
    # Resto del código igual...
    consultas = Consultas.objects.filter(pacienteid=ficha.pacienteid)\
        .select_related('personalid')\
        .order_by('-fechaconsulta')
    
    for consulta in consultas:
        consulta.servicios = Consultaservicios.objects.filter(consultaid=consulta.consultaid)\
            .select_related('servicioid')
    
    hospitalizaciones = Hospitalizaciones.objects.filter(pacienteid=ficha.pacienteid)\
        .select_related('habitacionid', 'habitacionid__tipohabitacionid', 'tipoaltaid', 'personalid')\
        .order_by('-fechaingreso')
    
    for hosp in hospitalizaciones:
        hosp.servicios = Hospitalizacionservicios.objects.filter(hospitalizacionid=hosp.hospitalizacionid)\
            .select_related('servicioid')
    
    return render(request, 'enfermeria/Paciente/Historial/VerHistorial.html', {
        'ficha': ficha,
        'signos_vitales': signos_dict,
        'enfermera_responsable': enfermera_responsable,
        'doctor_responsable': doctor_responsable,
        'consultas': consultas,
        'hospitalizaciones': hospitalizaciones
    })


def vista_hospitalizacion_enfermeria(request):
    """Vista que muestra todas las hospitalizaciones activas en forma de tabla (para enfermería)."""
    if not request.session.get('usuario_id') or request.session.get('rol') != 'Enfermería':
        return redirect('login')

    try:
        hospitalizaciones = Hospitalizaciones.objects.filter(
            estado=True
        ).select_related('pacienteid', 'habitacionid', 'habitacionid__tipohabitacionid')

        return render(request, 'enfermeria/Hospitalizacion/Hospitalizacion.html', {
            'hospitalizaciones': hospitalizaciones
        })

    except Exception as e:
        print(f"❌ Error al cargar hospitalizaciones: {e}")
        return redirect('menu_enfermeria')
#
#Servicios de hospitalizaciones de enfermeria----------------------------------------------------------------------------
#
def servicios_hospitalizacion_enfermeria(request, id):
    """Vista para mostrar los servicios aplicados a una hospitalización (Enfermería)."""
    if not request.session.get('usuario_id') or request.session.get('rol') != 'Enfermería':
        return redirect('login')

    try:
        hospitalizacion = get_object_or_404(Hospitalizaciones, pk=id)

        servicios = Hospitalizacionservicios.objects.filter(
            hospitalizacionid=hospitalizacion
        ).select_related('servicioid', 'personalsolicitanteid')

        return render(request, 'enfermeria/Hospitalizacion/ServiciosHospitalizacion.html', {
            'hospitalizacion': hospitalizacion,
            'servicios': servicios
        })

    except Exception as e:
        print(f"❌ Error cargando servicios: {e}")
        return redirect('ver_hospitalizaciones_enfermeria') 
    
# ----------------------------
# PERFIL DEL PERSONAL LOGUEADO------------------------------------------------------------------------------------------------
# ----------------------------
def perfil_personal_enfermeria(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    personal_id = request.session.get('usuario_id')
    personal = get_object_or_404(Personal.objects.select_related('especialidadid'), personalid=personal_id)

    return render(request, 'enfermeria/Perfil.html', {
        'personal': personal
    })