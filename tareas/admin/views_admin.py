from django.shortcuts import render, redirect
from tareas.admin.Forms.form_personal import PersonalForm, PersonalEditForm
from tareas.admin.Forms.form_paciente import PacienteForm, PacienteEditForm
from tareas.admin.Forms.form_especialidad import EspecialidadForm
from tareas.admin.Forms.form_servicio import ServicioForm
from tareas.admin.Forms.form_habitacion import HabitacionForm, TipoHabitacionForm
from tareas.admin.Forms.form_metodo_pago import MetodoPagoForm
from tareas.admin.Forms.form_config import ConfiguracionForm
from tareas.admin.config_utils import load_config, save_config
from tareas.models import (
    Personal, Pacientes, PacienteAudit, Especialidades,
    Servicios, Facturas, Pagos, Consultas, Consultaservicios,
    Habitaciones, Tiposhabitacion, Metodospago
)
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.core.management import call_command
from io import StringIO
from django.utils import timezone
from django.db.models import Count, Sum
from django.db.models.functions import TruncDay
from django.contrib.sessions.models import Session
import csv
#-----------------------------------------------------
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from tareas.models import Pacientes  # Ajusta si tu modelo se llama diferente
import json
#------------------------------------------------------------
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from tareas.models import Pacientes, HuellaDactilar
import base64

@api_view(['POST'])
def registrar_huella(request):
    try:
        print("💻 LLEGÓ EL POST:", request.data)
        data = request.data
        pacienteid = data['pacienteid']
        mano = data['mano']
        dedo = data['dedo']
        template = base64.b64decode(data['template'])

        # Verificar que exista el paciente
        if not Pacientes.objects.filter(pacienteid=pacienteid).exists():
            return Response({'success': False, 'mensaje': 'Paciente no encontrado'}, status=404)

        # Verificar si ya existe la huella para ese dedo
        if HuellaDactilar.objects.filter(pacienteid=pacienteid, mano=mano, dedo=dedo).exists():
            return Response({'success': False, 'mensaje': 'Huella ya registrada para ese dedo.'}, status=400)

        # Crear la huella
        HuellaDactilar.objects.create(
            pacienteid=pacienteid,
            mano=mano,
            dedo=dedo,
            template=template,
            fecharegistro=timezone.now()
        )

        return Response({'success': True, 'mensaje': 'Huella registrada correctamente.'}, status=201)

    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
def resultado_biometrico(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            paciente_id = data.get("paciente_id")
            if not paciente_id:
                return JsonResponse({'status': 'error', 'message': 'paciente_id no enviado'})

            paciente = get_object_or_404(Pacientes, pacienteid=paciente_id)

            url = f"/admin/paciente/{paciente_id}/"  # Ahora apunta al perfil
            return JsonResponse({
                'status': 'success',
                'redirect_url': url
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'})

#------------------------------------------------------------
def dashboard_view(request):
    if 'usuario_id' not in request.session:
        return redirect('login')

    contexto = {
        'nombre': request.session.get('nombre'),
        'rol': request.session.get('rol')
    }
    return render(request, 'admin/MenuAdmin.html', contexto)


def registrar_personal(request):
    if request.method == 'POST':
        form = PersonalForm(request.POST)
        if form.is_valid():
            try:
                # Validar número de documento único
                if Personal.objects.filter(numerodocumento=form.cleaned_data['numerodocumento']).exists():
                    messages.error(request, "⚠️ El número de documento ya está registrado.")
                elif Personal.objects.filter(usuario=form.cleaned_data['usuario']).exists():
                    messages.error(request, "⚠️ El nombre de usuario ya está en uso.")
                else:
                    personal = form.save(commit=False)
                    personal.contrasena = make_password(personal.contrasena)
                    personal.save()
                    messages.success(request, "✅ Personal registrado exitosamente.")
                    return redirect('registrar_personal')
            except Exception as e:
                messages.error(request, f"❌ Error al guardar: {str(e)}")
        else:
            messages.error(request, "❌ Revisa los campos del formulario.")
    else:
        form = PersonalForm()

    contexto = {
        'form': form,
        'nombre': request.session.get('nombre'),
        'rol': request.session.get('rol'),
    }
    return render(request, 'admin/registrar_personal.html', contexto)


def listar_personal(request):
    personal = Personal.objects.all()
    return render(request, 'admin/listar_personal.html', {'personal': personal})


def editar_personal(request, personal_id):
    personal = Personal.objects.get(pk=personal_id)
    if request.method == 'POST':
        form = PersonalEditForm(request.POST, instance=personal)
        if form.is_valid():
            if Personal.objects.exclude(pk=personal_id).filter(
                numerodocumento=form.cleaned_data['numerodocumento']
            ).exists():
                messages.error(request, "⚠️ El número de documento ya está registrado.")
            elif Personal.objects.exclude(pk=personal_id).filter(
                usuario=form.cleaned_data['usuario']
            ).exists():
                messages.error(request, "⚠️ El nombre de usuario ya está en uso.")
            else:
                obj = form.save(commit=False)
                if form.cleaned_data['contrasena']:
                    obj.contrasena = make_password(form.cleaned_data['contrasena'])
                obj.save()
                messages.success(request, "✅ Datos actualizados correctamente.")
                return redirect('listar_personal')
        else:
            messages.error(request, "❌ Revisa los campos del formulario.")
    else:
        form = PersonalEditForm(instance=personal)
    contexto = {
        'form': form,
        'nombre': request.session.get('nombre'),
        'rol': request.session.get('rol'),
    }
    return render(request, 'admin/editar_personal.html', contexto)


def inactivar_personal(request, personal_id):
    """Marcar un miembro del personal como inactivo."""
    personal = Personal.objects.get(pk=personal_id)
    personal.estado = False
    personal.save()
    messages.success(request, 'Personal inactivado.')
    return redirect('listar_personal')


def reactivar_personal(request, personal_id):
    """Reactivar un miembro del personal."""
    personal = Personal.objects.get(pk=personal_id)
    personal.estado = True
    personal.save()
    messages.success(request, 'Personal reactivado.')
    return redirect('listar_personal')


def eliminar_personal(request, personal_id):
    """Eliminar definitivamente un registro de personal."""
    personal = Personal.objects.get(pk=personal_id)
    personal.delete()
    messages.success(request, 'Personal eliminado.')
    return redirect('listar_personal')


def registrar_paciente(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            if Pacientes.objects.filter(numerodocumento=form.cleaned_data['numerodocumento']).exists():
                messages.error(request, "⚠️ El número de documento ya está registrado.")
                contexto = {
                    'form': form,
                    'nombre': request.session.get('nombre'),
                    'rol': request.session.get('rol')
                }
                return render(request, 'admin/registrar_paciente.html', contexto)
            else:
                paciente = form.save()
                messages.success(request, "✅ Paciente registrado exitosamente. ID: {}".format(paciente.pacienteid))
                contexto = {
                    'form': PacienteForm(),  # Formulario vacío para un nuevo registro
                    'nombre': request.session.get('nombre'),
                    'rol': request.session.get('rol'),
                    'pacienteid': paciente.pacienteid
                }
                return render(request, 'admin/registrar_paciente.html', contexto)
        else:
            messages.error(request, "❌ Revisa los campos del formulario.")
            contexto = {
                'form': form,
                'nombre': request.session.get('nombre'),
                'rol': request.session.get('rol')
            }
            return render(request, 'admin/registrar_paciente.html', contexto)
    else:
        form = PacienteForm()
        contexto = {
            'form': form,
            'nombre': request.session.get('nombre'),
            'rol': request.session.get('rol')
        }
        return render(request, 'admin/registrar_paciente.html', contexto)




def listar_pacientes(request):
    pacientes = Pacientes.objects.all()
    query = request.GET.get('q')
    if query:
        pacientes = pacientes.filter(nombres__icontains=query) | pacientes.filter(apellidos__icontains=query) | pacientes.filter(numerodocumento__icontains=query)

    sexo = request.GET.get('sexo')
    if sexo:
        pacientes = pacientes.filter(genero=sexo)


    estado = request.GET.get('estado')
    if estado in ['activo', 'inactivo']:
        pacientes = pacientes.filter(estado=(estado == 'activo'))

    paginator = Paginator(pacientes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    contexto = {
        'page_obj': page_obj,
        'nombre': request.session.get('nombre'),
        'rol': request.session.get('rol'),
        'q': query or '',
        'sexo': sexo or '',
        'estado': estado or '',
    }
    return render(request, 'admin/listar_pacientes.html', contexto)


def ver_paciente(request, paciente_id):
    paciente = Pacientes.objects.get(pk=paciente_id)
    contexto = {'paciente': paciente, 'nombre': request.session.get('nombre'), 'rol': request.session.get('rol')}
    return render(request, 'admin/ver_paciente.html', contexto)

def editar_paciente(request, paciente_id):
    paciente = Pacientes.objects.get(pk=paciente_id)
    
    if request.method == 'POST':
        form = PacienteEditForm(request.POST, instance=paciente)
        if form.is_valid():
            if Pacientes.objects.exclude(pk=paciente_id).filter(numerodocumento=form.cleaned_data['numerodocumento']).exists():
                messages.error(request, "⚠️ El número de documento ya está registrado.")
            else:
                form.save()
                messages.success(request, "✅ Datos actualizados correctamente.")
                contexto = {
                    'form': form,
                    'nombre': request.session.get('nombre'),
                    'rol': request.session.get('rol'),
                    'pacienteid': paciente.pacienteid
                }
                return render(request, 'admin/editar_paciente.html', contexto)
        else:
            messages.error(request, "❌ Revisa los campos del formulario.")
    else:
        form = PacienteEditForm(instance=paciente)
    
    contexto = {
        'form': form,
        'nombre': request.session.get('nombre'),
        'rol': request.session.get('rol'),
        'pacienteid': paciente.pacienteid
    }
    return render(request, 'admin/editar_paciente.html', contexto)



def inactivar_paciente(request, paciente_id):
    paciente = Pacientes.objects.get(pk=paciente_id)
    paciente.estado = False
    paciente.save()
    PacienteAudit.objects.create(paciente=paciente, usuario=request.session.get('nombre'), accion='inactivar')
    messages.success(request, "Paciente inactivado.")
    return redirect('listar_pacientes')


def reactivar_paciente(request, paciente_id):
    paciente = Pacientes.objects.get(pk=paciente_id)
    paciente.estado = True
    paciente.save()
    PacienteAudit.objects.create(paciente=paciente, usuario=request.session.get('nombre'), accion='reactivar')
    messages.success(request, "Paciente reactivado.")
    return redirect('listar_pacientes')


def exportar_pacientes(request):
    pacientes = Pacientes.objects.all()
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="pacientes.csv"'
    writer = csv.writer(response)
    writer.writerow(['Nombre Completo', 'CI', 'Edad', 'Genero', 'Grupo sanguineo', 'Alergias', 'Estado'])
    for p in pacientes:
        writer.writerow([
            f"{p.nombres} {p.apellidos}",
            p.numerodocumento,
            p.edad or '',
            p.genero or '',
            p.gruposanguineo or '',
            p.alergias or '',
            'Activo' if p.estado else 'Inactivo'
        ])
    return response


# ----------------------------
# GESTIÓN DE ESPECIALIDADES
# ----------------------------
def listar_especialidades(request):
    especialidades = Especialidades.objects.all()
    return render(request, 'admin/listar_especialidades.html', {
        'especialidades': especialidades,
        'nombre': request.session.get('nombre'),
        'rol': request.session.get('rol'),
    })


def registrar_especialidad(request):
    if request.method == 'POST':
        form = EspecialidadForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Especialidad guardada correctamente.')
            return redirect('listar_especialidades')
        else:
            messages.error(request, 'Revisa los campos del formulario.')
    else:
        form = EspecialidadForm()
    return render(request, 'admin/registrar_especialidad.html', {
        'form': form,
        'nombre': request.session.get('nombre'),
        'rol': request.session.get('rol'),
    })


def editar_especialidad(request, especialidad_id):
    especialidad = Especialidades.objects.get(pk=especialidad_id)
    if request.method == 'POST':
        form = EspecialidadForm(request.POST, instance=especialidad)
        if form.is_valid():
            form.save()
            messages.success(request, 'Especialidad actualizada.')
            return redirect('listar_especialidades')
        else:
            messages.error(request, 'Revisa los campos del formulario.')
    else:
        form = EspecialidadForm(instance=especialidad)
    return render(request, 'admin/registrar_especialidad.html', {
        'form': form,
        'nombre': request.session.get('nombre'),
        'rol': request.session.get('rol'),
    })


def eliminar_especialidad(request, especialidad_id):
    """Eliminar una especialidad médica."""
    especialidad = Especialidades.objects.get(pk=especialidad_id)
    especialidad.delete()
    messages.success(request, 'Especialidad eliminada.')
    return redirect('listar_especialidades')


# ----------------------------
# GESTIÓN DE SERVICIOS MÉDICOS
# ----------------------------
def listar_servicios(request):
    servicios = Servicios.objects.all()
    return render(request, 'admin/listar_servicios.html', {
        'servicios': servicios,
        'nombre': request.session.get('nombre'),
        'rol': request.session.get('rol'),
    })


def registrar_servicio(request):
    if request.method == 'POST':
        form = ServicioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Servicio guardado correctamente.')
            return redirect('listar_servicios')
        else:
            messages.error(request, 'Revisa los campos del formulario.')
    else:
        form = ServicioForm()
    return render(request, 'admin/registrar_servicio.html', {
        'form': form,
        'nombre': request.session.get('nombre'),
        'rol': request.session.get('rol'),
    })


def editar_servicio(request, servicio_id):
    servicio = Servicios.objects.get(pk=servicio_id)
    if request.method == 'POST':
        form = ServicioForm(request.POST, instance=servicio)
        if form.is_valid():
            form.save()
            messages.success(request, 'Servicio actualizado.')
            return redirect('listar_servicios')
        else:
            messages.error(request, 'Revisa los campos del formulario.')
    else:
        form = ServicioForm(instance=servicio)
    return render(request, 'admin/registrar_servicio.html', {
        'form': form,
        'nombre': request.session.get('nombre'),
        'rol': request.session.get('rol'),
    })


def eliminar_servicio(request, servicio_id):
    """Eliminar un servicio médico."""
    servicio = Servicios.objects.get(pk=servicio_id)
    servicio.delete()
    messages.success(request, 'Servicio eliminado.')
    return redirect('listar_servicios')


# ----------------------------
# GESTIÓN DE HABITACIONES
# ----------------------------
def listar_habitaciones(request):
    habitaciones = Habitaciones.objects.all()
    return render(request, 'admin/listar_habitaciones.html', {
        'habitaciones': habitaciones,
        'nombre': request.session.get('nombre'),
        'rol': request.session.get('rol'),
    })


def registrar_habitacion(request):
    if request.method == 'POST':
        form = HabitacionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Habitación guardada correctamente.')
            return redirect('listar_habitaciones')
        else:
            messages.error(request, 'Revisa los campos del formulario.')
    else:
        form = HabitacionForm()
    return render(request, 'admin/registrar_habitacion.html', {
        'form': form,
        'nombre': request.session.get('nombre'),
        'rol': request.session.get('rol'),
    })


def editar_habitacion(request, habitacion_id):
    habitacion = Habitaciones.objects.get(pk=habitacion_id)
    if request.method == 'POST':
        form = HabitacionForm(request.POST, instance=habitacion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Habitación actualizada.')
            return redirect('listar_habitaciones')
        else:
            messages.error(request, 'Revisa los campos del formulario.')
    else:
        form = HabitacionForm(instance=habitacion)
    return render(request, 'admin/registrar_habitacion.html', {
        'form': form,
        'nombre': request.session.get('nombre'),
        'rol': request.session.get('rol'),
    })


def eliminar_habitacion(request, habitacion_id):
    habitacion = Habitaciones.objects.get(pk=habitacion_id)
    habitacion.delete()
    messages.success(request, 'Habitación eliminada.')
    return redirect('listar_habitaciones')


# ----------------------------
# GESTIÓN DE TIPOS DE HABITACIÓN
# ----------------------------
def listar_tipos_habitacion(request):
    tipos = Tiposhabitacion.objects.all()
    return render(request, 'admin/listar_tipos_habitacion.html', {
        'tipos': tipos,
        'nombre': request.session.get('nombre'),
        'rol': request.session.get('rol'),
    })


def registrar_tipohabitacion(request):
    if request.method == 'POST':
        form = TipoHabitacionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tipo de habitación guardado.')
            return redirect('listar_tipos_habitacion')
        else:
            messages.error(request, 'Revisa los campos del formulario.')
    else:
        form = TipoHabitacionForm()
    return render(request, 'admin/registrar_tipohabitacion.html', {
        'form': form,
        'nombre': request.session.get('nombre'),
        'rol': request.session.get('rol'),
    })


def editar_tipohabitacion(request, tipo_id):
    tipo = Tiposhabitacion.objects.get(pk=tipo_id)
    if request.method == 'POST':
        form = TipoHabitacionForm(request.POST, instance=tipo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tipo de habitación actualizado.')
            return redirect('listar_tipos_habitacion')
        else:
            messages.error(request, 'Revisa los campos del formulario.')
    else:
        form = TipoHabitacionForm(instance=tipo)
    return render(request, 'admin/registrar_tipohabitacion.html', {
        'form': form,
        'nombre': request.session.get('nombre'),
        'rol': request.session.get('rol'),
    })


def eliminar_tipohabitacion(request, tipo_id):
    tipo = Tiposhabitacion.objects.get(pk=tipo_id)
    tipo.delete()
    messages.success(request, 'Tipo de habitación eliminado.')
    return redirect('listar_tipos_habitacion')


# ----------------------------
# GESTIÓN DE MÉTODOS DE PAGO
# ----------------------------
def listar_metodos_pago(request):
    metodos = Metodospago.objects.all()
    return render(request, 'admin/listar_metodos_pago.html', {
        'metodos': metodos,
        'nombre': request.session.get('nombre'),
        'rol': request.session.get('rol'),
    })


def registrar_metodo_pago(request):
    if request.method == 'POST':
        form = MetodoPagoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Método de pago guardado.')
            return redirect('listar_metodos_pago')
        else:
            messages.error(request, 'Revisa los campos del formulario.')
    else:
        form = MetodoPagoForm()
    return render(request, 'admin/registrar_metodo_pago.html', {
        'form': form,
        'nombre': request.session.get('nombre'),
        'rol': request.session.get('rol'),
    })


def editar_metodo_pago(request, metodo_id):
    metodo = Metodospago.objects.get(pk=metodo_id)
    if request.method == 'POST':
        form = MetodoPagoForm(request.POST, instance=metodo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Método de pago actualizado.')
            return redirect('listar_metodos_pago')
        else:
            messages.error(request, 'Revisa los campos del formulario.')
    else:
        form = MetodoPagoForm(instance=metodo)
    return render(request, 'admin/registrar_metodo_pago.html', {
        'form': form,
        'nombre': request.session.get('nombre'),
        'rol': request.session.get('rol'),
    })


def eliminar_metodo_pago(request, metodo_id):
    metodo = Metodospago.objects.get(pk=metodo_id)
    metodo.delete()
    messages.success(request, 'Método de pago eliminado.')
    return redirect('listar_metodos_pago')


# ----------------------------
# HISTORIAL DE CONSULTAS
# ----------------------------
def historial_paciente(request, paciente_id):
    paciente = Pacientes.objects.get(pk=paciente_id)
    consultas = Consultas.objects.filter(pacienteid=paciente)
    return render(request, 'admin/historial_paciente.html', {
        'paciente': paciente,
        'consultas': consultas,
        'nombre': request.session.get('nombre'),
        'rol': request.session.get('rol'),
    })


# ----------------------------
# LISTADOS FINANCIEROS
# ----------------------------
def listar_facturas(request):
    facturas = Facturas.objects.all()
    return render(request, 'admin/listar_facturas.html', {
        'facturas': facturas,
        'nombre': request.session.get('nombre'),
        'rol': request.session.get('rol'),
    })


def listar_pagos(request):
    pagos = Pagos.objects.all()
    return render(request, 'admin/listar_pagos.html', {
        'pagos': pagos,
        'nombre': request.session.get('nombre'),
        'rol': request.session.get('rol'),
    })


# ----------------------------
# LISTADO DE CONSULTAS
# ----------------------------
def listar_consultas(request):
    consultas = Consultas.objects.select_related('pacienteid', 'personalid')
    doctor = request.GET.get('doctor')
    if doctor:
        consultas = consultas.filter(
            personalid__nombres__icontains=doctor
        ) | consultas.filter(personalid__apellidos__icontains=doctor)
    inicio = request.GET.get('inicio')
    if inicio:
        consultas = consultas.filter(fechaconsulta__date__gte=inicio)
    fin = request.GET.get('fin')
    if fin:
        consultas = consultas.filter(fechaconsulta__date__lte=fin)
    paginator = Paginator(consultas.order_by('-fechaconsulta'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'admin/listar_consultas.html', {
        'page_obj': page_obj,
        'doctor': doctor or '',
        'inicio': inicio or '',
        'fin': fin or '',
        'nombre': request.session.get('nombre'),
        'rol': request.session.get('rol'),
    })


def detalle_consulta(request, consulta_id):
    """Muestra la información completa de una consulta y sus servicios."""
    consulta = Consultas.objects.select_related('pacienteid', 'personalid').get(pk=consulta_id)
    servicios = Consultaservicios.objects.select_related('servicioid').filter(consultaid=consulta)
    return render(request, 'admin/detalle_consulta.html', {
        'consulta': consulta,
        'servicios': servicios,
        'nombre': request.session.get('nombre'),
        'rol': request.session.get('rol'),
    })


def reportes_estadisticas(request):
    """Vista con métricas simples de uso del sistema."""
    consultas_medico = Consultas.objects.values(
        'personalid__nombres', 'personalid__apellidos'
    ).annotate(total=Count('consultaid')).order_by('-total')[:10]
    total_facturado = Facturas.objects.aggregate(total=Sum('total'))['total'] or 0

    # Pacientes nuevos vs. recurrentes
    pacientes_consultas = Consultas.objects.values('pacienteid').annotate(total=Count('consultaid'))
    pacientes_nuevos = sum(1 for c in pacientes_consultas if c['total'] == 1)
    pacientes_recurrentes = sum(1 for c in pacientes_consultas if c['total'] > 1)

    # Consultas y facturación por día
    consultas_dia = Consultas.objects.annotate(dia=TruncDay('fechaconsulta')).values('dia').annotate(total=Count('consultaid')).order_by('dia')
    facturacion_dia = Facturas.objects.annotate(dia=TruncDay('fechaemision')).values('dia').annotate(total=Sum('total')).order_by('dia')

    return render(request, 'admin/reportes.html', {
        'consultas_medico': consultas_medico,
        'total_facturado': total_facturado,
        'consultas_dia': consultas_dia,
        'facturacion_dia': facturacion_dia,
        'pacientes_nuevos': pacientes_nuevos,
        'pacientes_recurrentes': pacientes_recurrentes,
        'nombre': request.session.get('nombre'),
        'rol': request.session.get('rol'),
    })


# ----------------------------
# CONTROL DE ACCESOS
# ----------------------------


def control_accesos(request):
    """Lista las sesiones activas mostrando el usuario y rol."""
    sesiones_activas = []
    for sesion in Session.objects.filter(expire_date__gte=timezone.now()):
        datos = sesion.get_decoded()
        if 'usuario_id' in datos:
            sesiones_activas.append({
                'nombre': datos.get('nombre', 'Desconocido'),
                'rol': datos.get('rol', ''),
                'ultimo_acceso': sesion.expire_date,
            })
    return render(request, 'admin/control_accesos.html', {
        'sesiones': sesiones_activas,
        'nombre': request.session.get('nombre'),
        'rol': request.session.get('rol'),
    })


# ----------------------------
# CONFIGURACIONES GENERALES
# ----------------------------

def configuraciones_generales(request):
    """Permite editar parámetros básicos almacenados en config.json."""
    config = load_config()
    if request.method == 'POST':
        form = ConfiguracionForm(request.POST)
        if form.is_valid():
            config['nombre_clinica'] = form.cleaned_data['nombre_clinica']
            config['logo_url'] = form.cleaned_data['logo_url']
            save_config(config)
            messages.success(request, 'Configuración guardada.')
            return redirect('configuraciones_generales')
    else:
        form = ConfiguracionForm(initial=config)
    return render(request, 'admin/configuraciones.html', {
        'form': form,
        'nombre': request.session.get('nombre'),
        'rol': request.session.get('rol'),
        'config': config,
    })


def descargar_backup(request):
    """Devuelve un volcado JSON de la base de datos."""
    buffer = StringIO()
    call_command('dumpdata', '--natural-foreign', stdout=buffer)
    response = HttpResponse(buffer.getvalue(), content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="backup.json"'
    return response
