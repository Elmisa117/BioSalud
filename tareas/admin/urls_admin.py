from django.urls import path
from .views_admin import dashboard_view
from .views_admin import dashboard_view, registrar_personal, listar_personal


urlpatterns = [
    path('', dashboard_view, name='admin_dashboard'),
    path('registrar_personal/', registrar_personal, name='registrar_personal'),
    path('listar_personal/', listar_personal, name='listar_personal'),
]
