from django.shortcuts import render, redirect
from django.db import connection
from django.http import JsonResponse
from tareas.models import Personal  # o el nombre correcto de tu modelo

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

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT personalid, rol, nombres, apellidos
                FROM personal
                WHERE usuario = %s AND contrasena = %s
            """, [usuario, contrasena])
            personal = cursor.fetchone()

        if personal:
            # Guardamos datos en sesión
            request.session['usuario_id'] = personal[0]
            request.session['rol'] = personal[1]
            request.session['nombre'] = personal[2] + " " + personal[3]
            # Retornamos JSON para que el JS haga la redirección
            return JsonResponse({'rol': personal[1]}, status=200)
        else:
            return JsonResponse({'error': 'Usuario o contraseña incorrectos'}, status=401)

    return render(request, 'login.html')

def panel_cajero(request):
    usuario = request.user.username  # o request.session['usuario'] si manejas login personalizado

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
