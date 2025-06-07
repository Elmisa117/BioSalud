from django.urls import path, include
from .views import login_view, cerrar_sesion

urlpatterns = [
    path('', login_view, name='login'),
    path('cerrar/', cerrar_sesion, name='cerrar_sesion'),
    # path('inicio/', inicio_view, name='inicio'),

    # Rutas de cada módulo por rol
    path('admin/', include('tareas.admin.urls_admin')),
    path('doctor/', include('tareas.doctor.urls_doctor')),
    path('enfermeria/', include('tareas.enfermeria.urls_enfermeria')),
    path('cajero/', include('tareas.cajero.urls_cajero')),
]
