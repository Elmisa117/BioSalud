from django.shortcuts import render, redirect
from tareas.admin.Forms.form_personal import PersonalForm
from tareas.models import Personal, Pacientes, PacienteAudit
from tareas.admin.Forms.form_paciente import PacienteForm, PacienteEditForm
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse
import csv

def dashboard_view(request):
    if 'usuario_id' not in request.session:
        return redirect('login')

    contexto = {
        'nombre': request.session.get('nombre'),
        'rol': request.session.get('rol')
    }
    return render(request, 'admin/MenuAdmin.html', contexto)

from django.contrib import messages  # 👈 Importar mensajes

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


def registrar_paciente(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            if Pacientes.objects.filter(numerodocumento=form.cleaned_data['numerodocumento']).exists():
                messages.error(request, "⚠️ El número de documento ya está registrado.")
            else:
                paciente = form.save(commit=False)
                paciente.save()
                PacienteAudit.objects.create(paciente=paciente, usuario=request.session.get('nombre'), accion='crear')
                messages.success(request, "✅ Paciente registrado exitosamente.")
                return redirect('registrar_paciente')
        else:
            messages.error(request, "❌ Revisa los campos del formulario.")
    else:
        form = PacienteForm()
    contexto = {
        'form': form,
        'nombre': request.session.get('nombre'),
        'rol': request.session.get('rol'),
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

    seguro = request.GET.get('seguro')
    if seguro:
        pacientes = pacientes.filter(seguro__icontains=seguro)

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
        'seguro': seguro or '',
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
                PacienteAudit.objects.create(paciente=paciente, usuario=request.session.get('nombre'), accion='editar')
                messages.success(request, "✅ Datos actualizados correctamente.")
                return redirect('listar_pacientes')
        else:
            messages.error(request, "❌ Revisa los campos del formulario.")
    else:
        form = PacienteEditForm(instance=paciente)
    contexto = {'form': form, 'nombre': request.session.get('nombre'), 'rol': request.session.get('rol')}
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
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="pacientes.csv"'
    writer = csv.writer(response)
    writer.writerow(['Nombre Completo', 'CI', 'Edad', 'Genero', 'Seguro', 'Estado'])
    for p in pacientes:
        writer.writerow([
            f"{p.nombres} {p.apellidos}",
            p.numerodocumento,
            p.edad or '',
            p.genero or '',
            p.seguro or '',
            'Activo' if p.estado else 'Inactivo'
        ])
    return response
