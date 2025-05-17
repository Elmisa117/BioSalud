from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect

from tareas.views import (
    login_view,
    inicio_view,
    perfil_view,
    cerrar_sesion,
    registrar_paciente
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('login')),               # Redirige la raíz a /login/
    path('login/', login_view, name='login'),                  # Página de login
    path('inicio/', inicio_view, name='inicio'),               # Pantalla principal tras login
    path('perfil/', perfil_view, name='perfil'),               # Perfil del profesional logueado
    path('cerrar/', cerrar_sesion, name='cerrar'),             # Cierre de sesión
    path('registrar_paciente/', registrar_paciente, name='registrar_paciente'),  # Registro de pacientes
]


