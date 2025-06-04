from django.shortcuts import render
from tareas.models import RegistroProfesional


def dashboard_view(request):
    return render(request, 'admin/MenuAdmin.html')


def personal_list(request):
    personal = RegistroProfesional.objects.all()
    return render(request, 'admin/gestion_personal.html', {'personal': personal})
