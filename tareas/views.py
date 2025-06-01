from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
#from .models import Profesional  # Asegúrate que sea el modelo correcto

from django.contrib.auth.decorators import login_required

@login_required
def pantalla_principal(request):
    profesional = request.user  # Esto accede al usuario autenticado
    return render(request, 'PantallaPrincipal.html', {
        'profesional': profesional
    })

def login_view(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        contrasena = request.POST.get('contrasena')

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id_profesional, rol, nombres, apellidos
                FROM registro_profesional
                WHERE usuario = %s AND contrasena = %s
            """, [usuario, contrasena])
            profesional = cursor.fetchone()

        if profesional:
            request.session['usuario_id'] = profesional[0]
            request.session['rol'] = profesional[1]
            request.session['nombre'] = profesional[2] + " " + profesional[3]
            return redirect('inicio')
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")

    return render(request, 'login.html')


def inicio_view(request):
    if 'usuario_id' not in request.session:
        return redirect('login')
    return render(request, 'PantallaPrincipal.html', {
        'nombre': request.session.get('nombre'),
        'rol': request.session.get('rol')
    })

def perfil_view(request):
    if 'usuario_id' not in request.session:
        return redirect('login')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT p.nombres, p.apellidos, p.cedula_identidad, p.usuario, p.especialidad,
                   p.rol, p.activo, p.fecha_registro, h.nombre
            FROM registro_profesional p
            JOIN hospital h ON p.id_hospital = h.id_hospital
            WHERE p.id_profesional = %s
        """, [request.session['usuario_id']])
        profesional = cursor.fetchone()

    contexto = {
        'nombre': profesional[0] + " " + profesional[1],
        'ci': profesional[2],
        'usuario': profesional[3],
        'especialidad': profesional[4],
        'rol': profesional[5],
        'activo': "Sí" if profesional[6] else "No",
        'fecha': profesional[7],
        'hospital': profesional[8],
    }

    return render(request, 'perfil.html', contexto)
from django.shortcuts import redirect

def cerrar_sesion(request):
    request.session.flush()
    return redirect('login')


def registrar_paciente(request):
    if request.method == 'POST':
        datos = {
            'idioma_hablado': request.POST['idioma_hablado'],
            'cedula_identidad': request.POST['cedula_identidad'],
            'nombres': request.POST['nombres'],
            'apellidos': request.POST['apellidos'],
            'fecha_nacimiento': request.POST['fecha_nacimiento'],
            'sexo': request.POST['sexo'],
            'direccion': request.POST['direccion'],
            'telefono': request.POST['telefono'],
            'numero_emergencia': request.POST['numero_emergencia'],
            'correo': request.POST.get('correo', ''),
            'grupo_sanguineo': request.POST.get('grupo_sanguineo', ''),
            'alergias': request.POST.get('alergias', ''),
            'enfermedades_base': request.POST.get('enfermedades_base', ''),
            'fecha_registro': timezone.now(),
            'fecha_actualizacion': timezone.now()
        }

        # Insertar datos en la base de datos
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO registro_paciente (
                    idioma_hablado, cedula_identidad, nombres, apellidos, fecha_nacimiento, sexo,
                    direccion, telefono, numero_emergencia, correo, grupo_sanguineo,
                    alergias, enfermedades_base, fecha_registro, fecha_actualizacion
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, list(datos.values()))

        return redirect('inicio')  # Redirige a la pantalla principal después de guardar

    # Si es GET, muestra el formulario vacío
    return render(request, 'registro_paciente.html')

def pantalla_principal(request):
    return render(request, 'PantallaPrincipal.html')

# Nueva vista para cargar el formulario
def vista_formulario_paciente(request):
    return render(request, 'registro_paciente.html')