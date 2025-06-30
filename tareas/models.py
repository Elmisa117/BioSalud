# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

from django.db import models
import secrets

class DispositivoToken(models.Model):
    token = models.CharField(
        max_length=40,
        unique=True,
        editable=False
    )
    rol_autorizado = models.CharField(
        max_length=50,
        choices=[
            ('Administrador', 'Administrador'),
            ('Doctor', 'Doctor'),
            ('Enfermeria', 'Enfermeria'),
            ('Caja', 'Caja')
        ]
    )
    descripcion = models.CharField(max_length=100, blank=True, null=True)
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'dispositivo_token'
        verbose_name = 'Dispositivo Token'
        verbose_name_plural = 'Dispositivos Tokens'

    def __str__(self):
        return f"{self.descripcion or 'Dispositivo'} - {self.rol_autorizado}"

    def save(self, *args, **kwargs):
        if not self.token:
            while True:
                token = secrets.token_hex(20)
                if not DispositivoToken.objects.filter(token=token).exists():
                    self.token = token
                    break
        super().save(*args, **kwargs)


class Consultas(models.Model):
    consultaid = models.AutoField(primary_key=True)
    pacienteid = models.ForeignKey('Pacientes', models.DO_NOTHING, db_column='pacienteid')
    personalid = models.ForeignKey('Personal', models.DO_NOTHING, db_column='personalid')
    fechaconsulta = models.DateTimeField()
    motivocita = models.CharField(max_length=255, blank=True, null=True)
    diagnostico = models.TextField(blank=True, null=True)
    tratamiento = models.TextField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    costo = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fecharegistro = models.DateTimeField(blank=True, null=True)
    estado = models.BooleanField(blank=True, null=True)
    facturado = models.BooleanField(blank=True, null=True)  # ✅ Campo necesario para facturación

    class Meta:
        managed = False
        db_table = 'consultas'


class Consultaservicios(models.Model):
    consultaservicioid = models.AutoField(primary_key=True)
    consultaid = models.ForeignKey(Consultas, models.DO_NOTHING, db_column='consultaid')
    servicioid = models.ForeignKey('Servicios', models.DO_NOTHING, db_column='servicioid')
    cantidad = models.IntegerField()
    fechaservicio = models.DateTimeField()
    observaciones = models.CharField(max_length=255, blank=True, null=True)
    fecharegistro = models.DateTimeField(blank=True, null=True)
    estado = models.BooleanField(blank=True, null=True)
    facturado = models.BooleanField(blank=True, null=True)  # ✅ NUEVO CAMPO

    class Meta:
        managed = False
        db_table = 'consultaservicios'



class Cuotasplanpago(models.Model):
    cuotaid = models.AutoField(primary_key=True)
    planpagoid = models.ForeignKey('Planespago', models.DO_NOTHING, db_column='planpagoid')
    numerocuota = models.IntegerField()
    montocuota = models.DecimalField(max_digits=10, decimal_places=2)
    fechavencimiento = models.DateField()
    fechapago = models.DateTimeField(blank=True, null=True)
    pagoid = models.ForeignKey('Pagos', models.DO_NOTHING, db_column='pagoid', blank=True, null=True)
    estado = models.CharField(max_length=20, blank=True, null=True)
    fecharegistro = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cuotasplanpago'


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Especialidades(models.Model):
    especialidadid = models.AutoField(primary_key=True)
    nombreespecialidad = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    fechacreacion = models.DateTimeField(blank=True, null=True)
    estado = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return self.nombreespecialidad

    class Meta:
        managed = False
        db_table = 'especialidades'



class Facturas(models.Model):
    facturaid = models.AutoField(primary_key=True)
    pacienteid = models.ForeignKey('Pacientes', models.DO_NOTHING, db_column='pacienteid')
    numerofactura = models.CharField(max_length=20)
    fechaemision = models.DateTimeField()
    fechavencimiento = models.DateTimeField(blank=True, null=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    impuesto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    consultaid = models.ForeignKey(Consultas, models.DO_NOTHING, db_column='consultaid', blank=True, null=True)
    hospitalizacionid = models.ForeignKey('Hospitalizaciones', models.DO_NOTHING, db_column='hospitalizacionid', blank=True, null=True)
    observaciones = models.CharField(max_length=255, blank=True, null=True)
    fecharegistro = models.DateTimeField(blank=True, null=True)
    estado = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'facturas'


class Fichaclinico(models.Model):
    fichaid = models.AutoField(primary_key=True)
    pacienteid = models.ForeignKey('Pacientes', models.DO_NOTHING, db_column='pacienteid')
    personalid = models.ForeignKey('Personal', models.DO_NOTHING, db_column='personalid')
    fechaapertura = models.DateTimeField(blank=True, null=True)
    motivoconsulta = models.TextField(blank=True, null=True)
    diagnosticoinicial = models.TextField(blank=True, null=True)
    antecedentespersonales = models.TextField(blank=True, null=True)
    antecedentesfamiliares = models.TextField(blank=True, null=True)
    signosvitales = models.JSONField(blank=True, null=True)
    tratamientosugerido = models.TextField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=20, blank=True, null=True)
    tipoatencion = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'fichaclinico'


class Habitaciones(models.Model):
    habitacionid = models.AutoField(primary_key=True)
    numero = models.CharField(max_length=20)
    tipohabitacionid = models.ForeignKey('Tiposhabitacion', models.DO_NOTHING, db_column='tipohabitacionid')
    capacidad = models.IntegerField(blank=True, null=True)
    disponible = models.BooleanField(blank=True, null=True)
    fechacreacion = models.DateTimeField(blank=True, null=True)
    estado = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'habitaciones'


class Hospitalizaciones(models.Model):
    hospitalizacionid = models.AutoField(primary_key=True)
    pacienteid = models.ForeignKey('Pacientes', models.DO_NOTHING, db_column='pacienteid')
    habitacionid = models.ForeignKey(Habitaciones, models.DO_NOTHING, db_column='habitacionid')
    personalid = models.ForeignKey('Personal', models.DO_NOTHING, db_column='personalid')
    fechaingreso = models.DateTimeField()
    fechaalta = models.DateTimeField(blank=True, null=True)
    tipoaltaid = models.ForeignKey('Tiposalta', models.DO_NOTHING, db_column='tipoaltaid', blank=True, null=True)
    diagnostico = models.TextField(blank=True, null=True)
    tratamientoaplicado = models.TextField(blank=True, null=True)
    motivohospitalizacion = models.CharField(max_length=255, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    fecharegistro = models.DateTimeField(blank=True, null=True)
    estado = models.BooleanField(blank=True, null=True)
    facturado = models.BooleanField(blank=True, null=True)  # ✅ NUEVO CAMPO

    class Meta:
        managed = False
        db_table = 'hospitalizaciones'



class Hospitalizacionservicios(models.Model):
    hospitalizacionservicioid = models.AutoField(primary_key=True)

    # ✅ Relación con hospitalización
    hospitalizacionid = models.ForeignKey(
        'Hospitalizaciones',  # Modelo relacionado
        models.DO_NOTHING,
        db_column='hospitalizacionid',
        related_name='servicios_hospitalizacion'  # Opcional, útil para consultas inversas
    )

    # ✅ Relación con servicio
    servicioid = models.ForeignKey(
        'Servicios',
        models.DO_NOTHING,
        db_column='servicioid'
    )

    cantidad = models.IntegerField()
    fechaservicio = models.DateTimeField()
    observaciones = models.CharField(max_length=255, blank=True, null=True)

    # ✅ Personal que solicitó el servicio
    personalsolicitanteid = models.ForeignKey(
        'Personal',
        models.DO_NOTHING,
        db_column='personalsolicitanteid',
        blank=True,
        null=True
    )

    fecharegistro = models.DateTimeField(blank=True, null=True)
    estado = models.BooleanField(blank=True, null=True)
    facturado = models.BooleanField(blank=True, null=True)  # ✅ ya incluido

    class Meta:
        managed = False
        db_table = 'hospitalizacionservicios'




class Metodospago(models.Model):
    metodopagoid = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    requiereverificacion = models.BooleanField(blank=True, null=True)
    fechacreacion = models.DateTimeField(blank=True, null=True)
    estado = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'metodospago'


class Pacientes(models.Model):
    pacienteid = models.AutoField(primary_key=True)
    
    # Datos personales
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    numerodocumento = models.CharField(max_length=20)
    tipodocumento = models.CharField(max_length=20, blank=True, null=True)
    fechanacimiento = models.DateField(blank=True, null=True)
    edad = models.IntegerField(blank=True, null=True)
    genero = models.CharField(max_length=1, blank=True, null=True)

    # Contacto
    direccion = models.CharField(max_length=200, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)

    # Salud
    gruposanguineo = models.CharField(max_length=5, blank=True, null=True)
    alergias = models.TextField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    # Registro
    fecharegistro = models.DateTimeField(blank=True, null=True)
    estado = models.BooleanField(default=True)

    class Meta:
        managed = False  # Si usas una tabla existente
        db_table = 'pacientes'
        unique_together = (('numerodocumento', 'tipodocumento'),)


class HuellaDactilar(models.Model):
    huellaid = models.AutoField(primary_key=True)
    pacienteid = models.IntegerField()
    mano = models.CharField(max_length=10)
    dedo = models.CharField(max_length=20)
    template = models.BinaryField()
    fecharegistro = models.DateTimeField()

    class Meta:
        managed = False  # Impide que Django la modifique
        db_table = 'huellasdactilares'  # 👈 Exactamente como está en la BD



class PacienteAudit(models.Model):
    paciente = models.ForeignKey(Pacientes, on_delete=models.CASCADE)
    usuario = models.CharField(max_length=100)
    accion = models.CharField(max_length=50)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'paciente_audit'


class Pagos(models.Model):
    pagoid = models.AutoField(primary_key=True)
    facturaid = models.ForeignKey(Facturas, models.DO_NOTHING, db_column='facturaid')
    metodopagoid = models.ForeignKey(Metodospago, models.DO_NOTHING, db_column='metodopagoid')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fechapago = models.DateTimeField()
    numeroreferencia = models.CharField(max_length=100, blank=True, null=True)
    observaciones = models.CharField(max_length=255, blank=True, null=True)
    fecharegistro = models.DateTimeField(blank=True, null=True)
    estado = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pagos'


class Personal(models.Model):
    personalid = models.AutoField(primary_key=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    numerodocumento = models.CharField(max_length=20, unique=True)
    tipodocumento = models.CharField(max_length=20, blank=True, null=True)
    fechanacimiento = models.DateField(blank=True, null=True)
    genero = models.CharField(max_length=1, blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    fechaingreso = models.DateField()
    rol = models.CharField(max_length=50)
    especialidadid = models.ForeignKey(Especialidades, models.DO_NOTHING, db_column='especialidadid', blank=True, null=True)
    usuario = models.CharField(unique=True, max_length=50)
    contrasena = models.CharField(max_length=255)
    fechacreacion = models.DateTimeField(blank=True, null=True)
    estado = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'personal'


class Planespago(models.Model):
    planpagoid = models.AutoField(primary_key=True)
    facturaid = models.ForeignKey(Facturas, models.DO_NOTHING, db_column='facturaid')
    fechainicio = models.DateField()
    fechafin = models.DateField()
    numerocuotas = models.IntegerField()
    montototal = models.DecimalField(max_digits=10, decimal_places=2)
    observaciones = models.CharField(max_length=255, blank=True, null=True)
    fecharegistro = models.DateTimeField(blank=True, null=True)
    estado = models.CharField(max_length=20, blank=True, null=True)
    frecuencia = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'planespago'


class Servicios(models.Model):
    servicioid = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    costopacienteasegurado = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    requiereprescripcion = models.BooleanField(blank=True, null=True)
    fechacreacion = models.DateTimeField(blank=True, null=True)
    estado = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'servicios'


class Tiposalta(models.Model):
    tipoaltaid = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    fechacreacion = models.DateTimeField(blank=True, null=True)
    estado = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tiposalta'


class Tiposhabitacion(models.Model):
    tipohabitacionid = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    costodiario = models.DecimalField(max_digits=10, decimal_places=2)
    fechacreacion = models.DateTimeField(blank=True, null=True)
    estado = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tiposhabitacion'
