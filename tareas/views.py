from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.hashers import check_password
from tareas.models import Personal

#Biometrico------------------------------------------------------------
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Pacientes, DispositivoToken
from django.utils.timezone import now

@csrf_exempt
def resultado_biometrico(request):
    if request.method == 'POST':
        try:
            # Obtener token
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Token '):
                return JsonResponse({'status': 'error', 'message': 'Token no proporcionado'}, status=401)

            token_value = auth_header.split(' ')[1]
            dispositivo = get_object_or_404(DispositivoToken, token=token_value, activo=True)

            # Leer body
            data = json.loads(request.body)
            paciente_id = data.get('paciente_id')

            if not paciente_id:
                return JsonResponse({'status': 'error', 'message': 'paciente_id no proporcionado'}, status=400)

            # Verificar paciente
            get_object_or_404(Pacientes, pacienteid=paciente_id)

            # Generar URL según rol
            rol_urls = {
                "Administrador": f"/admin/paciente/{paciente_id}/",
                "Doctor": f"/Doctor/pacientes/perfil/{paciente_id}/",
                "Enfermeria": f"/enfermeria/pacientes/perfil/{paciente_id}/",
                "Caja": f"/cajero/ver_paciente/{paciente_id}/"
            }

            # Buscar el rol y su URL
            rol_autorizado = dispositivo.rol_autorizado
            url = rol_urls.get(rol_autorizado)

            if not url:
                return JsonResponse({'status': 'error', 'message': f'Rol no reconocido: {rol_autorizado}'}, status=400)

            # Log opcional
            print(f"[{now()}] Token OK: {dispositivo.descripcion}, Rol: {rol_autorizado}, Paciente: {paciente_id}")

            return JsonResponse({'status': 'success', 'redirect_url': url})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'JSON inválido'}, status=400)
        except DispositivoToken.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Token inválido o inactivo'}, status=401)
        except Exception as e:
            print(f"[{now()}] ERROR: {str(e)}")
            return JsonResponse({'status': 'error', 'message': 'Error interno'}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)



# ---------------------------
# API: REGISTRAR HUELLA DACTILAR
# ---------------------------
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import get_object_or_404
import base64
from .models import Pacientes, HuellaDactilar

@api_view(['POST'])  # Solo permite peticiones POST
def registrar_huella(request):
    """
    API para registrar una huella dactilar enviada desde la app C#.
    Esta API:
    - Recibe el ID del paciente, mano, dedo y la huella codificada en base64.
    - Verifica que el paciente exista.
    - Verifica que no exista ya una huella para ese dedo y mano.
    - Guarda la huella en la base de datos.
    """
    try:
        # Capturamos los datos que nos envía la app C#
        data = request.data
        pacienteid = data['pacienteid']  # ID del paciente
        mano = data['mano']              # Mano (ej: "derecha", "izquierda")
        dedo = data['dedo']              # Dedo (ej: "indice")
        template = base64.b64decode(data['template'])  # Decodificamos el template de base64 a binario

        # Verificamos si el paciente existe
        if not Pacientes.objects.filter(pacienteid=pacienteid).exists():
            # Si no existe, devolvemos un error 404
            return Response({'success': False, 'mensaje': 'Paciente no encontrado'}, status=404)

        # Verificamos si ya existe una huella registrada para ese dedo y mano en ese paciente
        if HuellaDactilar.objects.filter(pacienteid=pacienteid, mano=mano, dedo=dedo).exists():
            # Si ya hay, devolvemos un error 400
            return Response({'success': False, 'mensaje': 'Huella ya registrada para ese dedo.'}, status=400)

        # Guardamos la huella en la base de datos
        HuellaDactilar.objects.create(
            pacienteid=pacienteid,
            mano=mano,
            dedo=dedo,
            template=template,
            fecharegistro=timezone.now()  # Fecha y hora actual
        )

        # Devolvemos éxito con estado 201 (creado)
        return Response({'success': True, 'mensaje': 'Huella registrada correctamente.'}, status=201)

    except Exception as e:
        # Si ocurre un error inesperado, lo devolvemos como error 500
        return Response({'success': False, 'error': str(e)}, status=500)


# ----------------------------
# LOGIN CON REDIRECCIÓN POR ROL
# ----------------------------
def login_view(request):
    """
    Vista que autentica usuarios de la tabla 'personal'.
    Si las credenciales coinciden, guarda en sesión y responde con el rol para redirigir.
    """
    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        contrasena = request.POST.get('contrasena')

        try:
            personal = Personal.objects.get(usuario=usuario)

            if check_password(contrasena, personal.contrasena):
                # Guardar datos en sesión
                request.session['usuario_id'] = personal.personalid
                request.session['rol'] = personal.rol
                request.session['nombre'] = f"{personal.nombres} {personal.apellidos}"

                # Normalizar rol: Enfermera o Enfermería → Enfermería
                rol = personal.rol.strip().lower()
                if rol in ['enfermera', 'enfermería']:
                    rol_normalizado = 'Enfermería'
                else:
                    rol_normalizado = personal.rol

                return JsonResponse({'rol': rol_normalizado}, status=200)
            else:
                return JsonResponse({'error': 'Usuario o contraseña incorrectos'}, status=401)

        except Personal.DoesNotExist:
            return JsonResponse({'error': 'Usuario o contraseña incorrectos'}, status=401)

    return render(request, 'login.html')


# ----------------------------
# PANEL CAJERO (Ejemplo)
# ----------------------------
def panel_cajero(request):
    usuario = request.session.get('usuario')

    try:
        cajero = Personal.objects.get(usuario=usuario)
        nombre_completo = f"{cajero.nombres} {cajero.apellidos}"
    except Personal.DoesNotExist:
        nombre_completo = "Usuario"

    return render(request, 'cajero/panel_cajero.html', {
        'nombre': nombre_completo
    })


# ----------------------------
# CERRAR SESIÓN
# ----------------------------
def cerrar_sesion(request):
    """
    Limpia la sesión del usuario y lo redirige al login.
    """
    request.session.flush()
    return redirect('login')
