from django.contrib import admin
from .models import DispositivoToken

@admin.register(DispositivoToken)
class DispositivoTokenAdmin(admin.ModelAdmin):
    list_display = ('token', 'rol_autorizado', 'descripcion', 'activo', 'creado')
    readonly_fields = ('token',)