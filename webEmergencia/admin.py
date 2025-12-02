from django.contrib import admin
from .models import Persona, Paciente, Especialista, Consulta, Seguimiento
from django.contrib.auth.hashers import make_password


class PersonaAdmin(admin.ModelAdmin):
    """Admin personalizado para Persona que hashea automáticamente las contraseñas"""
    list_display = ('rut', 'nombre', 'apellido', 'correo')
    search_fields = ('rut', 'nombre', 'apellido')
    
    def save_model(self, request, obj, form, change):
        """Sobreescribe save_model para hashear la contraseña"""
        if obj.contrasena and not (
            obj.contrasena.startswith('pbkdf2_sha256$') or
            obj.contrasena.startswith('bcrypt$') or
            obj.contrasena.startswith('$2')
        ):
            obj.contrasena = make_password(obj.contrasena)
        
        super().save_model(request, obj, form, change)


admin.site.register(Persona, PersonaAdmin)
admin.site.register(Paciente)
admin.site.register(Especialista)
admin.site.register(Consulta)
admin.site.register(Seguimiento)