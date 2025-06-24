import json
from django.db import connection
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

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

    nombre = request.session.get('nombre_completo', 'Usuario')
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
            ORDER BY nombres ASC
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


# ----------------------------
# REGISTRAR O EDITAR PACIENTE
# ----------------------------
def registrar_paciente_enfermeria(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    paciente_id = request.GET.get('id')
    paciente_datos = {}

    if request.method == 'POST':
        paciente_id = request.POST.get('paciente_id')
        nombres = request.POST.get('nombres')
        apellidos = request.POST.get('apellidos')
        numero_documento = request.POST.get('numerodocumento')
        tipo_documento = request.POST.get('tipodocumento')
        fecha_nacimiento = request.POST.get('fechanacimiento')
        edad = request.POST.get('edad') or None
        genero = request.POST.get('genero')
        direccion = request.POST.get('direccion')
        telefono = request.POST.get('telefono')
        email = request.POST.get('email')
        grupo_sanguineo = request.POST.get('gruposanguineo')
        alergias = request.POST.get('alergias')
        observaciones = request.POST.get('observaciones')

        with connection.cursor() as cursor:
            if paciente_id:
                cursor.execute("""
                    UPDATE pacientes SET
                        nombres = %s, apellidos = %s, numerodocumento = %s, tipodocumento = %s,
                        fechanacimiento = %s, edad = %s, genero = %s, direccion = %s,
                        telefono = %s, email = %s, gruposanguineo = %s,
                        alergias = %s, observaciones = %s
                    WHERE pacienteid = %s
                """, [
                    nombres, apellidos, numero_documento, tipo_documento,
                    fecha_nacimiento or None, edad, genero, direccion,
                    telefono, email, grupo_sanguineo, alergias, observaciones,
                    paciente_id
                ])
            else:
                cursor.execute("""
                    INSERT INTO pacientes (
                        nombres, apellidos, numerodocumento, tipodocumento,
                        fechanacimiento, edad, genero, direccion, telefono,
                        email, gruposanguineo, alergias, observaciones,
                        fecharegistro, estado
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, TRUE)
                """, [
                    nombres, apellidos, numero_documento, tipo_documento,
                    fecha_nacimiento or None, edad, genero, direccion,
                    telefono, email, grupo_sanguineo, alergias, observaciones
                ])

        return redirect('vista_pacientes_enfermeria')

    if paciente_id:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT nombres, apellidos, numerodocumento, tipodocumento,
                       fechanacimiento, edad, genero, direccion, telefono,
                       email, gruposanguineo, alergias, observaciones
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
                    'observaciones': fila[12]
                }

    return render(request, 'enfermeria/Paciente/RegistrarPaciente/RegistrarPaciente.html', {
        'paciente': paciente_datos
    })


# ----------------------------
# REGISTRAR FICHA CLÍNICA
# ----------------------------
def ficha_clinico_enfermeria(request, id):
    paciente = get_object_or_404(Pacientes, pacienteid=id)
    doctores = Personal.objects.filter(rol='Doctor', estado=True).select_related('especialidadid')

    if request.method == 'POST':
        personal_id = request.POST.get('personal_id')
        motivo = request.POST.get('motivo')
        diagnostico = request.POST.get('diagnostico')
        antecedentes_personales = request.POST.get('antecedentes_personales')
        antecedentes_familiares = request.POST.get('antecedentes_familiares')

        signos_vitales = {
            'ta': request.POST.get('ta'),
            'fc': request.POST.get('fc'),
            'fr': request.POST.get('fr'),
            'temp': request.POST.get('temp'),
            'spo2': request.POST.get('spo2')
        }

        tratamiento = request.POST.get('tratamiento')
        observaciones = request.POST.get('observaciones')

        if personal_id and motivo:
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
                observaciones=observaciones
            )
            ficha.save()
            return redirect('vista_pacientes_enfermeria')
        else:
            messages.error(request, "Faltan campos obligatorios para registrar la ficha clínica.")

    return render(request, 'enfermeria/Paciente/FichaClinico/FichaClinico.html', {
        'paciente': paciente,
        'doctores': doctores
    })


# ----------------------------
# HISTORIAL CLÍNICO DEL PACIENTE
# ----------------------------
def historial_enfermeria(request, id):
    paciente = get_object_or_404(Pacientes, pacienteid=id)
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    fichas = Fichaclinico.objects.filter(pacienteid=paciente)

    if fecha_inicio:
        fichas = fichas.filter(fechaapertura__date__gte=fecha_inicio)
    if fecha_fin:
        fichas = fichas.filter(fechaapertura__date__lte=fecha_fin)

    fichas = fichas.order_by('-fechaapertura')

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
    ficha = get_object_or_404(Fichaclinico, fichaid=fichaid)

    doctor_responsable = None
    enfermera_responsable = None

    if ficha.personalid.rol.lower() == 'doctor':
        doctor_responsable = ficha.personalid
    elif ficha.personalid.rol.lower() == 'enfermera':
        enfermera_responsable = ficha.personalid

    consultas = Consultas.objects.filter(pacienteid=ficha.pacienteid).select_related('personalid').order_by('-fechaconsulta')
    for consulta in consultas:
        consulta.servicios = Consultaservicios.objects.filter(consultaid=consulta).select_related('servicioid')

    hospitalizaciones = Hospitalizaciones.objects.filter(pacienteid=ficha.pacienteid).select_related('habitacionid', 'habitacionid__tipohabitacionid', 'tipoaltaid', 'personalid').order_by('-fechaingreso')
    for hosp in hospitalizaciones:
        hosp.servicios = Hospitalizacionservicios.objects.filter(hospitalizacionid=hosp).select_related('servicioid')

    try:
        signos_dict = ficha.signosvitales or {}
    except Exception:
        signos_dict = {}

    return render(request, 'enfermeria/Paciente/Historial/VerHistorial.html', {
        'ficha': ficha,
        'consultas': consultas,
        'hospitalizaciones': hospitalizaciones,
        'doctor_responsable': doctor_responsable,
        'enfermera_responsable': enfermera_responsable,
        'signos_vitales': signos_dict
    })


# ----------------------------
# VISTA DE MAPA DE HABITACIONES
# ----------------------------
def vista_hospitalizacion_enfermeria(request):
    hospitalizaciones = Hospitalizaciones.objects.select_related('pacienteid', 'habitacionid', 'habitacionid__tipohabitacionid').filter(estado=True)

    camas_ocupadas = {}
    for h in hospitalizaciones:
        tipo = h.habitacionid.tipohabitacionid.nombre
        camas_ocupadas.setdefault(tipo, []).append({
            'nombre': f"{h.pacienteid.nombres} {h.pacienteid.apellidos}",
            'habitacion': h.habitacionid.numero,
            'ocupada': True
        })

    privadas = [{'habitacion': f'P{n}', 'ocupada': False} for n in range(1, 7)]
    suites = [{'habitacion': f'S{n}', 'ocupada': False} for n in range(1, 5)]
    salas = [{'habitacion': f'Sala1-{n}', 'ocupada': False} for n in range(1, 10)]

    def reemplazar(camas, tipo):
        for ocupada in camas_ocupadas.get(tipo, []):
            for cama in camas:
                if cama['habitacion'] == ocupada['habitacion']:
                    cama.update(ocupada)

    reemplazar(privadas, 'Privada')
    reemplazar(suites, 'Suite')
    reemplazar(salas, 'Sala')

    return render(request, 'enfermeria/Hospitalizacion/Hospitalizacion.html', {
        'privadas': privadas,
        'suites': suites,
        'salas': salas
    })


# ----------------------------
# PERFIL DEL PERSONAL LOGUEADO
# ----------------------------
def perfil_personal_enfermeria(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    personal_id = request.session.get('usuario_id')
    personal = get_object_or_404(Personal.objects.select_related('especialidadid'), personalid=personal_id)

    return render(request, 'enfermeria/Perfil.html', {
        'personal': personal
    })