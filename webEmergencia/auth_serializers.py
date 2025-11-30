from rest_framework import serializers
from .models import Persona, Paciente
from django.contrib.auth.hashers import make_password

class RegistroSerializer(serializers.Serializer):
    # Campos de Persona
    rut = serializers.CharField(max_length=10)
    nombre = serializers.CharField(max_length=100)
    apellido = serializers.CharField(max_length=100)
    correo = serializers.EmailField(max_length=100)
    contrasena = serializers.CharField(write_only=True, max_length=100)
    
    # Campos de Paciente
    fecha_nacimiento = serializers.DateField()
    telefono = serializers.CharField(max_length=20, required=False, allow_blank=True)
    direccion = serializers.CharField(max_length=100, required=False, allow_blank=True)

    def create(self, validated_data):
        # Crear persona primero
        persona_data = {
            'rut': validated_data['rut'],
            'nombre': validated_data['nombre'],
            'apellido': validated_data['apellido'],
            'correo': validated_data['correo'],
            'contrasena': make_password(validated_data['contrasena'])
        }
        persona = Persona.objects.create(**persona_data)

        # Crear paciente
        paciente_data = {
            'fk_rut': persona,
            'fecha_nacimiento': validated_data['fecha_nacimiento'],
            'telefono': validated_data.get('telefono', ''),
            'direccion': validated_data.get('direccion', '')
        }
        paciente = Paciente.objects.create(**paciente_data)

        return paciente