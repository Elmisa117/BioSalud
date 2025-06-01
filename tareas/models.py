from django.db import models

class RegistroProfesional(models.Model):
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    cedula_identidad = models.CharField(max_length=20)
    usuario = models.CharField(max_length=100, unique=True)
    contrasena = models.CharField(max_length=128)
    especialidad = models.CharField(max_length=100, blank=True, null=True)
    rol = models.CharField(max_length=50)
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateField(auto_now_add=True)
    id_hospital = models.IntegerField()

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"
