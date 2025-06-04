from django.shortcuts import render, redirect
from tareas.admin.Forms.form_personal import PersonalForm
from tareas.models import Personal
from django.contrib.auth.hashers import make_password
from django.contrib import messages  # 👈 Importar mensajes

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
