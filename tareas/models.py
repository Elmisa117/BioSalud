from django.db import models

class Especialidad(models.Model):
    especialidadid = models.AutoField(primary_key=True)
    nombreespecialidad = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    fechacreacion = models.DateTimeField(auto_now_add=True)
    estado = models.BooleanField(default=True)

    class Meta:
        db_table = 'especialidades'


class Personal(models.Model):
    personalid = models.AutoField(primary_key=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    numerodocumento = models.CharField(max_length=20)
    tipodocumento = models.CharField(max_length=20, default='CI')
    fechanacimiento = models.DateField(null=True, blank=True)
    genero = models.CharField(max_length=1, null=True, blank=True)
    direccion = models.CharField(max_length=200, null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    fechaingreso = models.DateField()
    rol = models.CharField(max_length=50)
    especialidadid = models.ForeignKey('Especialidad', models.SET_NULL, null=True, db_column='especialidadid')
    usuario = models.CharField(max_length=50, unique=True)
    contrasena = models.CharField(max_length=255)
    fechacreacion = models.DateTimeField(auto_now_add=True)
    estado = models.BooleanField(default=True)

    class Meta:
        db_table = 'personal'


class Paciente(models.Model):
    pacienteid = models.AutoField(primary_key=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    numerodocumento = models.CharField(max_length=20)
    tipodocumento = models.CharField(max_length=20, default='CI')
    fechanacimiento = models.DateField(null=True, blank=True)
    edad = models.IntegerField(null=True, blank=True)
    genero = models.CharField(max_length=1, null=True, blank=True)
    direccion = models.CharField(max_length=200, null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    gruposanguineo = models.CharField(max_length=5, null=True, blank=True)
    alergias = models.TextField(null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)
    fecharegistro = models.DateTimeField(auto_now_add=True)
    estado = models.BooleanField(default=True)

    class Meta:
        db_table = 'pacientes'
        constraints = [
            models.UniqueConstraint(fields=['numerodocumento', 'tipodocumento'], name='uq_numerodocumento')
        ]


class FichaClinico(models.Model):
    fichaid = models.AutoField(primary_key=True)
    paciente = models.ForeignKey('Paciente', models.CASCADE, db_column='pacienteid')
    personal = models.ForeignKey('Personal', models.CASCADE, db_column='personalid')
    fechaapertura = models.DateTimeField(auto_now_add=True)
    motivoconsulta = models.TextField(null=True, blank=True)
    diagnosticoinicial = models.TextField(null=True, blank=True)
    antecedentespersonales = models.TextField(null=True, blank=True)
    antecedentesfamiliares = models.TextField(null=True, blank=True)
    signosvitales = models.JSONField(null=True, blank=True)
    tratamientosugerido = models.TextField(null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)
    estado = models.CharField(max_length=20, default='Activa')

    class Meta:
        db_table = 'fichaclinico'


class Consulta(models.Model):
    consultaid = models.AutoField(primary_key=True)
    paciente = models.ForeignKey('Paciente', models.CASCADE, db_column='pacienteid')
    personal = models.ForeignKey('Personal', models.CASCADE, db_column='personalid')
    fechaconsulta = models.DateTimeField()
    motivocita = models.CharField(max_length=255, null=True, blank=True)
    diagnostico = models.TextField(null=True, blank=True)
    tratamiento = models.TextField(null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)
    costo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fecharegistro = models.DateTimeField(auto_now_add=True)
    estado = models.BooleanField(default=True)
    tipoconsulta = models.CharField(max_length=50)
    facturado = models.BooleanField(default=False)  # ✅ NUEVO CAMPO

    class Meta:
        db_table = 'consultas'



class ConsultaServicios(models.Model):
    consultaservicioid = models.AutoField(primary_key=True)
    consultaid = models.ForeignKey('Consulta', models.CASCADE, db_column='consultaid')
    servicioid = models.ForeignKey('Servicio', models.CASCADE, db_column='servicioid')
    cantidad = models.IntegerField(default=1)
    fechaservicio = models.DateTimeField()
    observaciones = models.CharField(max_length=255, null=True, blank=True)
    fecharegistro = models.DateTimeField(auto_now_add=True)
    estado = models.BooleanField(default=True)
    facturado = models.BooleanField(default=False)  # ✅ NUEVO CAMPO

    class Meta:
        db_table = 'consultaservicios'



class MetodoPago(models.Model):
    metodopagoid = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=255, null=True, blank=True)
    requiereverificacion = models.BooleanField(default=False)
    fechacreacion = models.DateTimeField(auto_now_add=True)
    estado = models.BooleanField(default=True)

    class Meta:
        db_table = 'metodospago'


class Factura(models.Model):
    facturaid = models.AutoField(primary_key=True)
    paciente = models.ForeignKey('Paciente', models.CASCADE, db_column='pacienteid')
    numerofactura = models.CharField(max_length=20)
    fechaemision = models.DateTimeField()
    fechavencimiento = models.DateTimeField(null=True, blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    impuesto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    consultaid = models.ForeignKey('Consulta', models.SET_NULL, null=True, blank=True, db_column='consultaid')
    hospitalizacionid = models.ForeignKey('Hospitalizacion', models.SET_NULL, null=True, blank=True, db_column='hospitalizacionid')
    observaciones = models.CharField(max_length=255, null=True, blank=True)
    fecharegistro = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, default='Pendiente')

    class Meta:
        db_table = 'facturas'


class Pago(models.Model):
    pagoid = models.AutoField(primary_key=True)
    factura = models.ForeignKey('Factura', models.CASCADE, db_column='facturaid')
    metodopago = models.ForeignKey('MetodoPago', models.CASCADE, db_column='metodopagoid')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fechapago = models.DateTimeField()
    numeroreferencia = models.CharField(max_length=100, null=True, blank=True)
    observaciones = models.CharField(max_length=255, null=True, blank=True)
    fecharegistro = models.DateTimeField(auto_now_add=True)
    estado = models.BooleanField(default=True)

    class Meta:
        db_table = 'pagos'


class Servicio(models.Model):
    servicioid = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=255, null=True, blank=True)
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    costopacienteasegurado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    requiereprescripcion = models.BooleanField(default=False)
    fechacreacion = models.DateTimeField(auto_now_add=True)
    estado = models.BooleanField(default=True)

    class Meta:
        db_table = 'servicios'


class TiposAlta(models.Model):
    tipoaltaid = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=255, null=True, blank=True)
    fechacreacion = models.DateTimeField(auto_now_add=True)
    estado = models.BooleanField(default=True)

    class Meta:
        db_table = 'tiposalta'


class TiposHabitacion(models.Model):
    tipohabitacionid = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=255, null=True, blank=True)
    costodiario = models.DecimalField(max_digits=10, decimal_places=2)
    fechacreacion = models.DateTimeField(auto_now_add=True)
    estado = models.BooleanField(default=True)

    class Meta:
        db_table = 'tiposhabitacion'


class Habitacion(models.Model):
    habitacionid = models.AutoField(primary_key=True)
    numero = models.CharField(max_length=20)
    tipohabitacion = models.ForeignKey('TiposHabitacion', models.CASCADE, db_column='tipohabitacionid')
    capacidad = models.IntegerField(default=1)
    disponible = models.BooleanField(default=True)
    fechacreacion = models.DateTimeField(auto_now_add=True)
    estado = models.BooleanField(default=True)

    class Meta:
        db_table = 'habitaciones'


class Hospitalizacion(models.Model):
    hospitalizacionid = models.AutoField(primary_key=True)
    paciente = models.ForeignKey('Paciente', models.CASCADE, db_column='pacienteid')
    habitacion = models.ForeignKey('Habitacion', models.CASCADE, db_column='habitacionid')
    personal = models.ForeignKey('Personal', models.CASCADE, db_column='personalid')
    fechaingreso = models.DateTimeField()
    fechaalta = models.DateTimeField(null=True, blank=True)
    tipoalta = models.ForeignKey('TiposAlta', models.SET_NULL, null=True, blank=True, db_column='tipoaltaid')
    diagnostico = models.TextField(null=True, blank=True)
    tratamientoaplicado = models.TextField(null=True, blank=True)
    motivohospitalizacion = models.CharField(max_length=255, null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)
    fecharegistro = models.DateTimeField(auto_now_add=True)
    estado = models.BooleanField(default=True)
    facturado = models.BooleanField(default=False)  # ✅ NUEVO CAMPO

    class Meta:
        db_table = 'hospitalizaciones'



class HospitalizacionServicios(models.Model):
    hospitalizacionservicioid = models.AutoField(primary_key=True)
    hospitalizacion = models.ForeignKey('Hospitalizacion', models.CASCADE, db_column='hospitalizacionid')
    servicioid = models.ForeignKey('Servicio', models.CASCADE, db_column='servicioid')
    cantidad = models.IntegerField(default=1)
    fechaservicio = models.DateTimeField()
    observaciones = models.CharField(max_length=255, null=True, blank=True)
    personalsolicitanteid = models.ForeignKey('Personal', models.SET_NULL, null=True, blank=True, db_column='personalsolicitanteid')
    fecharegistro = models.DateTimeField(auto_now_add=True)
    estado = models.BooleanField(default=True)

    class Meta:
        db_table = 'hospitalizacionservicios'


class PlanPago(models.Model):
    FRECUENCIAS = [
        ('semanal', 'Semanal'),
        ('quincenal', 'Quincenal'),
        ('mensual', 'Mensual'),
    ]

    planpagoid = models.AutoField(primary_key=True)
    factura = models.ForeignKey('Factura', models.CASCADE, db_column='facturaid')
    fechainicio = models.DateField()
    fechafin = models.DateField()
    numerocuotas = models.IntegerField()
    montototal = models.DecimalField(max_digits=10, decimal_places=2)
    frecuencia = models.CharField(max_length=20, choices=FRECUENCIAS, default='mensual')
    observaciones = models.CharField(max_length=255, null=True, blank=True)
    fecharegistro = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, default='Activo')

    class Meta:
        db_table = 'planespago'
        


class CuotaPlanPago(models.Model):
    cuotaid = models.AutoField(primary_key=True, db_column='cuotaid')
    planpago = models.ForeignKey('PlanPago', models.CASCADE, db_column='planpagoid', related_name='cuotas')
    numerocuota = models.IntegerField()
    fechavencimiento = models.DateField()
    montocuota = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, default='Pendiente')
    fecharegistro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cuotasplanpago'
        ordering = ['numerocuota']
