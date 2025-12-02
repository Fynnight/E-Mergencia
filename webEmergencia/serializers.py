from rest_framework import serializers
from .models import Consulta, Paciente, Especialista, Persona, Diagnostico, Receta

class RecetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receta
        fields = ['id', 'medicamento', 'dosis', 'horario']


class DiagnosticoSerializer(serializers.ModelSerializer):
    recetas = RecetaSerializer(many=True, read_only=True)
    
    class Meta:
        model = Diagnostico
        fields = ['id', 'descripcion', 'es_cronico', 'nombre_enfermedad', 'fecha_emision', 'recetas']


class ConsultaSerializer(serializers.ModelSerializer):
    paciente_nombre = serializers.SerializerMethodField()
    paciente_rut = serializers.SerializerMethodField()
    paciente_correo = serializers.SerializerMethodField()
    especialista_nombre = serializers.SerializerMethodField()
    diagnostico_data = DiagnosticoSerializer(read_only=True)
    
    class Meta:
        model = Consulta
        fields = '__all__'
    
    def get_paciente_nombre(self, obj):
        try:
            return f"{obj.fk_idpaciente.fk_rut.nombre} {obj.fk_idpaciente.fk_rut.apellido}"
        except:
            return None
    
    def get_paciente_rut(self, obj):
        try:
            return obj.fk_idpaciente.fk_rut.rut
        except:
            return None
    
    def get_paciente_correo(self, obj):
        try:
            return obj.fk_idpaciente.fk_rut.correo
        except:
            return None
    
    def get_especialista_nombre(self, obj):
        try:
            if obj.especialista_asignado:
                return f"{obj.especialista_asignado.fk_rutp.nombre} {obj.especialista_asignado.fk_rutp.apellido}"
        except:
            pass
        return None