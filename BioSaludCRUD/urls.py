from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from tareas.views import vista_formulario_paciente



from tareas.views import (
    login_view,
    inicio_view,
    perfil_view,
    cerrar_sesion,
    registrar_paciente,
    pantalla_principal  # 👈 agrega esto
)

 
urlpatterns = [
    path('', lambda request: redirect('login')),               # Redirige la raíz a /login/
    path('login/', login_view, name='login'),                  # Página de login
    path('inicio/', inicio_view, name='inicio'),               # Pantalla principal tras login
    path('perfil/', perfil_view, name='perfil'),               # Perfil del profesional logueado
    path('cerrar/', cerrar_sesion, name='cerrar'),             # Cierre de sesión
    path('registrar_paciente/', registrar_paciente, name='registrar_paciente'),  # Registro de pacientes
    path('principal/', pantalla_principal, name='pantalla_principal'),
    path('vista_registrar_paciente/', vista_formulario_paciente, name='vista_formulario_paciente'),
]


