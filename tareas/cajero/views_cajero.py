from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F
from django.http import JsonResponse
from django.utils import timezone
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
import traceback
import json
from datetime import datetime
from django.db.models import F, Value, ExpressionWrapper, DecimalField
from datetime import date
from django.contrib import messages  # Asegúrate de tener esto arriba
from django.db.models import Q

from tareas.models import (
    Pacientes,
    Consultas,
    Consultaservicios,
    Hospitalizaciones,
    Hospitalizacionservicios,
    Metodospago,
    Facturas,
    Pagos,
    Planespago,
    Cuotasplanpago
)


# 📜 PANEL DEL CAJERO
def panel_cajero(request):
    if 'usuario_id' not in request.session:
        return redirect('login')
    nombre_completo = request.session.get('nombre', 'Cajero')
    return render(request, 'cajero/panel_cajero.html', {'nombre': nombre_completo})

# 📊 MENÚ DE REPORTES
def menu_reportes(request):
    return render(request, 'cajero/menu_reportes.html')

# 🔎 BUSCAR PACIENTE
def buscar_paciente_cajero(request):
    query = request.GET.get('q', '')
    pacientes = Pacientes.objects.filter(
        Q(nombres__icontains=query) |
        Q(apellidos__icontains=query) |
        Q(numerodocumento__icontains=query)  # <-- Aquí está el cambio
    ) if query else Pacientes.objects.all()
    return render(request, 'cajero/BuscarPaciente.html', {'pacientes': pacientes, 'query': query})

# 👁️ PERFIL DEL PACIENTE
def ver_paciente(request, id):
    paciente = get_object_or_404(Pacientes, pk=id)
    return render(request, 'cajero/PerfilPaciente.html', {'paciente': paciente})



def generar_factura(request, paciente_id):
    paciente = get_object_or_404(Pacientes, pk=paciente_id)

    # Consultas no facturadas
    consultas = Consultas.objects.filter(
        pacienteid=paciente,
        estado=True,
        facturado=False
    )
    consulta_ids = consultas.values_list('consultaid', flat=True)

    # Servicios de consultas no facturados
    consulta_servicios = Consultaservicios.objects.filter(
        consultaid_id__in=consulta_ids,
        estado=True,
        facturado=False
    )

    # Hospitalizaciones no facturadas
    hospitalizaciones = Hospitalizaciones.objects.filter(
        pacienteid=paciente,
        estado=True,
        facturado=False
    )
    hosp_ids = hospitalizaciones.values_list('hospitalizacionid', flat=True)

    # Servicios de hospitalización no facturados
    hospitalizacion_servicios = Hospitalizacionservicios.objects.filter(
        hospitalizacionid_id__in=hosp_ids,
        estado=True,
        facturado=False
    )

    # Verificar si no hay ningún servicio
    if not (consultas.exists() or consulta_servicios.exists() or hospitalizaciones.exists() or hospitalizacion_servicios.exists()):
        messages.warning(request, "⚠️ El paciente no tiene servicios pendientes para facturar.")
        return redirect('ver_paciente', id=paciente.pacienteid)

    # Métodos de pago activos
    metodos_pago = Metodospago.objects.filter(estado=True)

    return render(request, 'cajero/GenerarFactura.html', {
        'paciente': paciente,
        'metodos_pago': metodos_pago,
        'consultas': consultas,
        'consulta_servicios': consulta_servicios,
        'hospitalizaciones': hospitalizaciones,
        'hospitalizacion_servicios': hospitalizacion_servicios,
        'fecha_emision': timezone.now(),  # ✅ Agregado
    })



# 📅 GUARDAR FACTURA Y PLAN DE PAGO
@csrf_exempt
def guardar_factura_y_plan(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        paciente_id = request.POST.get('paciente_id')
        paciente = Pacientes.objects.get(pk=paciente_id)
        hoy = timezone.now().date()

        numero_factura = request.POST.get('numeroFactura')
        fecha_emision = timezone.now()
        subtotal = float(request.POST.get('total', 0))
        monto_pagado = float(request.POST.get('montoPagado', 0))
        metodo_id = request.POST.get('metodoPago')
        numero_referencia = request.POST.get('numeroReferencia', '')
        observaciones = request.POST.get('observaciones', '')
        estado_factura = 'Pendiente' if monto_pagado < subtotal else 'Pagada'

        factura = Facturas.objects.create(
            pacienteid=paciente,
            numerofactura=numero_factura,
            fechaemision=fecha_emision,
            subtotal=subtotal,
            descuento=0,
            impuesto=0,
            total=subtotal,
            observaciones=observaciones,
            estado=estado_factura
        )

        metodo_pago = Metodospago.objects.get(pk=metodo_id)
        Pagos.objects.create(
            factura=factura,
            metodopago=metodo_pago,
            monto=monto_pagado,
            fechapago=fecha_emision,
            numeroreferencia=numero_referencia,
            observaciones=observaciones
        )

        # Marcar como facturado
        Consultas.objects.filter(
            pacienteid=paciente,
            estado=True,
            facturado=False,
            fechaconsulta__date=hoy
        ).update(facturado=True)

        consulta_ids = Consultas.objects.filter(
            pacienteid=paciente,
            estado=True,
            fechaconsulta__date=hoy
        ).values_list('consultaid', flat=True)

        Consultaservicios.objects.filter(
            consultaid_id__in=consulta_ids,
            estado=True,
            facturado=False,
            fechaservicio__date=hoy
        ).update(facturado=True)

        Hospitalizaciones.objects.filter(
            pacienteid=paciente,
            estado=True,
            facturado=False,
            fechaingreso__date=hoy
        ).update(facturado=True)

        hosp_ids = Hospitalizaciones.objects.filter(
            pacienteid=paciente,
            fechaingreso__date=hoy
        ).values_list('hospitalizacionid', flat=True)

        Hospitalizacionservicios.objects.filter(
            hospitalizacionid_id__in=hosp_ids,
            estado=True,
            facturado=False,
            fechaservicio__date=hoy
        ).update(facturado=True)

        # Plan de pago
        if request.POST.get('planPagoActivado') == 'true':
            planes_anteriores = Planespago.objects.filter(factura__paciente=paciente)
            tiene_pendientes = Cuotasplanpago.objects.filter(
                planpago__in=planes_anteriores,
                estado='Pendiente'
            ).exists()

            if tiene_pendientes:
                return JsonResponse({
                    'error': 'El paciente ya tiene un plan de pago con cuotas pendientes. No puede registrar uno nuevo.'
                }, status=400)

            numero_cuotas = int(request.POST.get('planNumeroCuotas'))
            fecha_inicio = request.POST.get('planFechaInicio')
            fecha_fin = request.POST.get('planFechaFin')
            frecuencia = request.POST.get('frecuencia', 'mensual')
            cuotas_json = request.POST.get('planCuotasJSON')

            plan = Planespago.objects.create(
                factura=factura,
                fechainicio=fecha_inicio,
                fechafin=fecha_fin,
                numerocuotas=numero_cuotas,
                montototal=subtotal - monto_pagado,
                frecuencia=frecuencia,
                observaciones="Generado automáticamente",
                estado='Activo'
            )

            cuotas = json.loads(cuotas_json)
            for i, cuota in enumerate(cuotas, start=1):
                Cuotasplanpago.objects.create(
                    planpago=plan,
                    numerocuota=i,
                    fechavencimiento=cuota['fecha'],
                    montocuota=cuota['monto'],
                    estado='Pendiente'
                )

        return JsonResponse({
            'mensaje': 'Factura y pagos registrados correctamente',
            'redirect_url': reverse('ver_paciente', args=[paciente.pacienteid])
        })

    except Exception as e:
        print("🚨 Error al guardar factura y plan de pago:")
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=400)


def verificar_servicios_json(request, paciente_id):
    print(f"🔍 Verificando servicios para paciente {paciente_id} en fecha: {date.today()}")

    # Consultas no facturadas
    consultas = Consultas.objects.filter(
        pacienteid=paciente_id,
        facturado=False,
        estado=True
    )
    print(f"📋 Consultas encontradas: {consultas.count()}")

    # Servicios de hospitalización no facturados, accediendo al paciente a través de la relación
    hospitalizacion_servicios = Hospitalizacionservicios.objects.filter(
        hospitalizacionid__pacienteid=paciente_id,
        facturado=False,
        estado=True
    )
    print(f"🏥 Servicios de hospitalización encontrados: {hospitalizacion_servicios.count()}")

    tiene_servicios = consultas.exists() or hospitalizacion_servicios.exists()
    print(f"✅ Tiene servicios: {tiene_servicios}")

    if tiene_servicios:
        return JsonResponse({'status': 'ok'})
    else:
        return JsonResponse({
            'status': 'empty',
            'mensaje': 'El paciente no tiene servicios pendientes para facturar.'
        })
    
# 📜 FUNCIÓN AUXILIAR: RESUMEN DE SERVICIOS DE UNA FACTURA
def resumen_servicios_factura(factura):
    try:
        resumenes = set()

        consultas = Consultas.objects.filter(paciente=factura.paciente, estado=True)
        for c in consultas:
            resumenes.add(f"Consulta {c.tipoconsulta}")

        consulta_ids = consultas.values_list('consultaid', flat=True)
        consulta_servicios = Consultaservicios.objects.filter(
            consultaid_id__in=consulta_ids, estado=True
        ).select_related('servicioid')

        for cs in consulta_servicios:
            resumenes.add(cs.servicioid.descripcion)

        hospitalizaciones = Hospitalizaciones.objects.filter(
            paciente=factura.paciente, estado=True
        ).select_related('habitacion__tipohabitacion')

        for h in hospitalizaciones:
            tipo = h.habitacion.tipohabitacion.nombre
            resumenes.add(f"Hospitalización {tipo}")

        lista = list(resumenes)
        return ", ".join(lista[:3]) if lista else "N/A"

    except Exception:
        return "N/A"

# ✅ VER PLAN DE PAGOS Y CUOTAS DEL PACIENTE
def ver_pagos_paciente(request, paciente_id):
    paciente = get_object_or_404(Pacientes, pk=paciente_id)

    # Obtener todos los planes de pago del paciente
    planes = Planespago.objects.filter(facturaid__pacienteid=paciente_id).prefetch_related('facturaid')

    metodos_pago = Metodospago.objects.filter(estado=True)

    planes_actualizados = []
    for plan in planes:
        # Obtener cuotas pendientes o pagadas ordenadas
        cuotas_ordenadas = plan.cuotasplanpago_set.filter(estado__in=['Pendiente', 'Pagada']).order_by('numerocuota')
        if cuotas_ordenadas.exists():
            plan.cuotas_ordenadas = cuotas_ordenadas
            plan.resumen_producto = resumen_servicios_factura(plan.facturaid)  # función que genera resumen visual
            planes_actualizados.append(plan)

    return render(request, 'cajero/VerPagosPaciente.html', {
        'paciente': paciente,
        'planes': planes_actualizados,
        'metodos_pago': metodos_pago
    })


# ✅ REGISTRAR PAGO DE UNA CUOTA
@csrf_exempt
def registrar_pago_cuota(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'mensaje': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
        cuota_id = data.get('cuota_id')
        monto = float(data.get('monto'))
        metodo_id = int(data.get('metodo_pago_id'))

        cuota = get_object_or_404(Cuotasplanpago, pk=cuota_id)
        metodo = get_object_or_404(Metodospago, pk=metodo_id)

        if cuota.estado != 'Pendiente':
            return JsonResponse({'status': 'error', 'mensaje': 'La cuota ya fue pagada o no es válida.'})

        # ✅ Corrección aquí: planpagoid es el nombre real del campo
        cuotas_anteriores = Cuotasplanpago.objects.filter(
            planpagoid=cuota.planpagoid,
            numerocuota__lt=cuota.numerocuota
        ).exclude(estado='Pagada')

        if cuotas_anteriores.exists():
            return JsonResponse({
                'status': 'error',
                'mensaje': 'Debe pagar las cuotas anteriores antes de esta.'
            })

        # ✅ También usamos cuota.planpagoid.facturaid para obtener la factura asociada
        pago = Pagos.objects.create(
            factura=cuota.planpagoid.facturaid,
            metodopago=metodo,
            monto=monto,
            fechapago=timezone.now(),
            numeroreferencia='Pago Manual desde Cuota',
            observaciones='Registro desde VerPagosPaciente'
        )

        cuota.estado = 'Pagada'
        cuota.fechapago = timezone.now()
        cuota.pagoid = pago  # ✅ Enlazar la cuota con el pago registrado
        cuota.save()

        return JsonResponse({'status': 'ok', 'mensaje': 'Pago registrado correctamente'})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'status': 'error', 'mensaje': str(e)}, status=500)
    
# ✅ BUSCAR PACIENTES EN TIEMPO REAL (JSON)
def buscar_pacientes_json(request):
    query = request.GET.get('q', '')
    pacientes = Pacientes.objects.filter(
        Q(nombres__icontains=query) |
        Q(apellidos__icontains=query) |
        Q(numerodocumento__icontains=query)
    )[:20]  # Limitar a 20 resultados opcionalmente

    data = []
    for p in pacientes:
        data.append({
            'id': p.pacienteid,
            'nombres': p.nombres,
            'apellidos': p.apellidos,
            'ci': p.numerodocumento,
            'fechanacimiento': p.fechanacimiento.strftime('%b. %d, %Y'),
            'telefono': p.telefono,
            'url': reverse('ver_paciente', args=[p.pacienteid])
        })

    return JsonResponse({'pacientes': data})

def ver_facturas_pagadas(request, paciente_id):
    paciente = get_object_or_404(Pacientes, pacienteid=paciente_id)
    facturas = Facturas.objects.filter(pacienteid=paciente, estado='Pagado')

    return render(request, 'cajero/ver_facturas_pagadas.html', {
        'paciente': paciente,
        'facturas': facturas,
    })

# ✅ ANULAR FACTURA
def anular_factura(request, factura_id):
    factura = get_object_or_404(Facturas, pk=factura_id)
    factura.estado = 'Anulada'
    factura.save()
    messages.success(request, f"Factura #{factura.numerofactura} anulada correctamente.")
    return redirect('ver_paciente', id=factura.paciente.pacienteid)



@csrf_exempt
def api_factura(request, paciente_id):
    try:
        print(f"🔍 Verificando servicios para paciente {paciente_id}")
        # Consultas no facturadas
        consultas = Consultas.objects.filter(pacienteid=paciente_id, facturado=False)
        consultas_data = [
            {
                'consulta_id': c.consultaid,
                'fecha': c.fechaconsulta.strftime('%Y-%m-%d'),
                'motivo': c.motivocita,
                'precio': float(c.costo or 0)
            }
            for c in consultas
        ]
        print(f"📋 Consultas encontradas: {len(consultas_data)}")

        # Servicios de consulta no facturados
        consulta_servicios = Consultaservicios.objects.filter(
            consultaid__pacienteid=paciente_id, facturado=False
        ).select_related('servicioid')
        consulta_servicios_data = [
            {
                'servicio__nombre': cs.servicioid.nombre,
                'servicio__costo': float(cs.servicioid.costo or 0)
            }
            for cs in consulta_servicios
        ]

        # Hospitalizaciones no facturadas
        hospitalizaciones = Hospitalizaciones.objects.filter(
            pacienteid=paciente_id,
            facturado=False
        ).select_related('habitacionid__tipohabitacionid')
        hospitalizaciones_data = []
        for h in hospitalizaciones:
            if not h.fechaingreso:
                continue
            fecha_alta = h.fechaalta or datetime.now()
            dias = max((fecha_alta.date() - h.fechaingreso.date()).days, 1)
            costo_diario = h.habitacionid.tipohabitacionid.costodiario
            total = dias * float(costo_diario)
            hospitalizaciones_data.append({
                'hospitalizacion_id': h.hospitalizacionid,
                'motivo': h.motivohospitalizacion,
                'dias': dias,
                'costo_diario': float(costo_diario),
                'total': round(total, 2)
            })
        print(f"🏥 Hospitalizaciones encontradas: {len(hospitalizaciones_data)}")

        # Servicios de hospitalización no facturados
        hosp_servicios = Hospitalizacionservicios.objects.filter(
            hospitalizacionid__pacienteid=paciente_id,
            facturado=False
        ).select_related('servicioid')
        hosp_servicios_data = [
            {
                'servicio__nombre': hs.servicioid.nombre,
                'servicio__costo': float(hs.servicioid.costo or 0)
            }
            for hs in hosp_servicios
        ]

        tiene_servicios = any([consultas_data, consulta_servicios_data, hospitalizaciones_data, hosp_servicios_data])
        print(f"✅ Tiene servicios: {tiene_servicios}")

        return JsonResponse({
            'consultas': consultas_data,
            'consultaservicios': consulta_servicios_data,
            'hospitalizaciones': hospitalizaciones_data,
            'hospitalizacionservicios': hosp_servicios_data,
            'tiene_servicios': tiene_servicios
        })

    except Exception as e:
        print(f"❌ Error en api_factura: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
