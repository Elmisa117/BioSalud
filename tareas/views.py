from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.hashers import check_password
from .models import Personal

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
                # Guardamos datos en sesión
                request.session['usuario_id'] = personal.personalid
                request.session['rol'] = personal.rol
                request.session['nombre'] = personal.nombres + " " + personal.apellidos
                # Retornamos JSON para que el JS haga la redirección
                return JsonResponse({'rol': personal.rol}, status=200)
            else:
                return JsonResponse({'error': 'Usuario o contraseña incorrectos'}, status=401)
        except Personal.DoesNotExist:
            return JsonResponse({'error': 'Usuario o contraseña incorrectos'}, status=401)

    return render(request, 'login.html')


# ----------------------------
# CERRAR SESIÓN
# ----------------------------
def cerrar_sesion(request):
    """
    Limpia la sesión del usuario y lo redirige al login.
    """
    request.session.flush()
    return redirect('login')
