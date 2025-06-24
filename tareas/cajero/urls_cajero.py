from django.urls import path
from . import views_cajero

urlpatterns = [
    # 🧾 Panel principal del cajero
    path('', views_cajero.panel_cajero, name='panel_cajero'),

    # 📊 Menú de reportes del cajero
    path('reportes/', views_cajero.menu_reportes, name='menu_reportes'),

    # 🔎 Buscar y ver paciente
    path('buscar_paciente_cajero/', views_cajero.buscar_paciente_cajero, name='buscar_paciente'),
    path('ver_paciente/<int:id>/', views_cajero.ver_paciente, name='ver_paciente'),
    path('buscar_pacientes_json/', views_cajero.buscar_pacientes_json, name='buscar_pacientes_json'),

    # 📄 Facturación
    path('generar_factura/<int:paciente_id>/', views_cajero.generar_factura, name='generar_factura'),
    path('guardar_factura/', views_cajero.guardar_factura_y_plan, name='guardar_factura'),
    path('verificar_servicios/<int:paciente_id>/', views_cajero.verificar_servicios_json, name='verificar_servicios'),
    path('api/factura2/<int:paciente_id>/', views_cajero.api_factura, name='api_factura'),

    # 🧾 Historial de facturas y pagos
    path('ver_pagos/<int:paciente_id>/', views_cajero.ver_pagos_paciente, name='ver_pagos_paciente'),
    path('paciente/<int:paciente_id>/facturas-pagadas/', views_cajero.ver_facturas_pagadas, name='ver_facturas_pagadas'),

    # 💰 Pagos y anulación
    path('registrar_pago_cuota/', views_cajero.registrar_pago_cuota, name='registrar_pago_cuota'),
    path('factura/<int:factura_id>/anular/', views_cajero.anular_factura, name='anular_factura'),
]
