from django.urls import path, include
from django.shortcuts import redirect
from tareas.views import login_view, cerrar_sesion

urlpatterns = [
    path('', lambda request: redirect('login')),  # Redirige raíz al login
    
    # Autenticación
    path('login/', login_view, name='login'),
    path('cerrar/', cerrar_sesion, name='cerrar'),


    # Rutas por módulo (rol)
    path('admin/', include('tareas.admin.urls_admin')),
    path('doctor/', include('tareas.doctor.urls_doctor')),
    path('enfermeria/', include('tareas.enfermeria.urls_enfermeria')),
    path('cajero/', include('tareas.cajero.urls_cajero')),
]


