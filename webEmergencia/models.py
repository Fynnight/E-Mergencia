from django.db import models


class Consulta(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aceptada', 'Aceptada'),
        ('cancelada', 'Cancelada'),
        ('aplazada', 'Aplazada'),
        ('finalizada', 'Finalizada'),
    ]
    
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    fk_idpaciente = models.ForeignKey('Paciente', models.DO_NOTHING, db_column='FK_IDPACIENTE')  # Field name made lowercase.
    fk_idespecialista = models.ForeignKey('Especialista', models.DO_NOTHING, db_column='FK_IDESPECIALISTA', blank=True, null=True, related_name='consultas')  # Field name made lowercase.
    motivo = models.CharField(db_column='MOTIVO', max_length=255)  # Field name made lowercase.
    sintomas = models.CharField(db_column='SINTOMAS', max_length=255, blank=True, null=True)  # Field name made lowercase.
    fecha_inicio = models.DateTimeField(db_column='FECHA_INICIO', blank=True, null=True)  # Field name made lowercase.
    diagnostico = models.CharField(db_column='DIAGNOSTICO', max_length=255, blank=True, null=True)  # Field name made lowercase.
    especialidad = models.CharField(db_column='ESPECIALIDAD', max_length=100, default='Medicina General')  # Field name made lowercase.
    estado = models.CharField(db_column='ESTADO', max_length=20, choices=ESTADO_CHOICES, default='pendiente')  # Field name made lowercase.
    especialista_asignado = models.ForeignKey('Especialista', models.SET_NULL, db_column='ESPECIALISTA_ASIGNADO', blank=True, null=True, related_name='citas_asignadas')  # Field name made lowercase.
    razon_cancelacion = models.TextField(db_column='RAZON_CANCELACION', blank=True, null=True)  # Field name made lowercase.

    class Meta:
         
        db_table = 'consulta'


class Especialista(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    fk_rutp = models.OneToOneField('Persona', models.DO_NOTHING, db_column='FK_RUTP')  # Field name made lowercase.
    especialidad = models.CharField(db_column='ESPECIALIDAD', max_length=100)  # Field name made lowercase.

    class Meta:
         
        db_table = 'especialista'


class Paciente(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    fk_rut = models.OneToOneField('Persona', models.DO_NOTHING, db_column='FK_RUT')  # Field name made lowercase.
    fecha_nacimiento = models.DateField(db_column='FECHA_NACIMIENTO')  # Field name made lowercase.
    telefono = models.CharField(db_column='TELEFONO', max_length=20, blank=True, null=True)  # Field name made lowercase.
    direccion = models.CharField(db_column='DIRECCION', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
         
        db_table = 'paciente'


class Persona(models.Model):
    rut = models.CharField(db_column='RUT', primary_key=True, max_length=10)  # Field name made lowercase.
    nombre = models.CharField(db_column='NOMBRE', max_length=100)  # Field name made lowercase.
    apellido = models.CharField(db_column='APELLIDO', max_length=100)  # Field name made lowercase.
    correo = models.CharField(db_column='CORREO', unique=True, max_length=100)  # Field name made lowercase.
    contrasena = models.CharField(db_column='CONTRASENA', max_length=100)  # Field name made lowercase.

    class Meta:
         
        db_table = 'persona'


class Seguimiento(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    fk_idpac = models.ForeignKey(Paciente, models.DO_NOTHING, db_column='FK_IDPAC')  # Field name made lowercase.
    medicacion = models.CharField(db_column='MEDICACION', max_length=100)  # Field name made lowercase.
    instruccion = models.CharField(db_column='INSTRUCCION', max_length=255)  # Field name made lowercase.
    control = models.CharField(db_column='CONTROL', max_length=255, blank=True, null=True)  # Field name made lowercase.
    fecha_registro = models.DateTimeField(db_column='FECHA_REGISTRO', blank=True, null=True)  # Field name made lowercase.
    dispositivo = models.CharField(db_column='DISPOSITIVO', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
         
        db_table = 'seguimiento'


class Diagnostico(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    consulta = models.OneToOneField(Consulta, models.CASCADE, db_column='FK_CONSULTA', related_name='diagnostico_data')
    descripcion = models.TextField(db_column='DESCRIPCION')
    es_cronico = models.BooleanField(db_column='ES_CRONICO', default=False)
    nombre_enfermedad = models.CharField(db_column='NOMBRE_ENFERMEDAD', max_length=255, null=True, blank=True)
    fecha_emision = models.DateTimeField(db_column='FECHA_EMISION', auto_now_add=True)

    class Meta:
        db_table = 'diagnostico'

    def __str__(self):
        return f"Diagnostico {self.id} - {self.descripcion[:50]}"


class Receta(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    diagnostico = models.ForeignKey(Diagnostico, models.CASCADE, db_column='FK_DIAGNOSTICO', related_name='recetas')
    medicamento = models.CharField(db_column='MEDICAMENTO', max_length=255)
    dosis = models.CharField(db_column='DOSIS', max_length=255)
    horario = models.CharField(db_column='HORARIO', max_length=255)

    class Meta:
        db_table = 'receta'

    def __str__(self):
        return f"{self.medicamento} - {self.dosis}"

def __str__(self):
    return str(self.xx) + " " + self.xxxx + "(SCORE: " + str(self.score) + ")"