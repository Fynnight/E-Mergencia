from django import forms
from .models import Persona, Paciente, Consulta

class VerificarRutForm(forms.Form):
    rut = forms.CharField(max_length=10, label='RUT',
                         widget=forms.TextInput(attrs={'class': 'form-control',
                                                     'placeholder': 'Ingrese su RUT'}))

class RegistroCompletoForm(forms.ModelForm):
    ESPECIALIDADES = [
        ('Medicina General', 'Medicina General'),
        ('Pediatría', 'Pediatría'),
        ('Cardiología', 'Cardiología'),
        ('Dermatología', 'Dermatología'),
        ('Oftalmología', 'Oftalmología'),
        ('Traumatología', 'Traumatología'),
    ]

    fecha_nacimiento = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    telefono = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    direccion = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    motivo = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    sintomas = forms.CharField(max_length=255, required=False, widget=forms.Textarea(attrs={'class': 'form-control'}))
    fecha_inicio = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}))
    especialidad = forms.ChoiceField(
        choices=ESPECIALIDADES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Persona
        fields = ['rut', 'nombre', 'apellido', 'correo']
        widgets = {
            'rut': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class CitaForm(forms.ModelForm):
    ESPECIALIDADES = [
        ('Medicina General', 'Medicina General'),
        ('Pediatría', 'Pediatría'),
        ('Cardiología', 'Cardiología'),
        ('Dermatología', 'Dermatología'),
        ('Oftalmología', 'Oftalmología'),
        ('Traumatología', 'Traumatología'),
    ]
    
    especialidad = forms.ChoiceField(
        choices=ESPECIALIDADES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Consulta
        fields = ['motivo', 'sintomas', 'fecha_inicio', 'especialidad']
        widgets = {
            'motivo': forms.TextInput(attrs={'class': 'form-control'}),
            'sintomas': forms.Textarea(attrs={'class': 'form-control'}),
            'fecha_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }