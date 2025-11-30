from django.contrib.auth import login, logout, authenticate
from django.shortcuts import redirect
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password
from .models import Persona, Paciente, Especialista
from .auth_serializers import RegistroSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    rut = request.data.get('rut')
    contrasena = request.data.get('contrasena')
    
    try:
        # Primero intenta autenticar con Django User (si existe)
        user = User.objects.get(username=rut)
        
        # Autentica con Django
        user_auth = authenticate(request, username=rut, password=contrasena)
        if user_auth is not None:
            login(request, user_auth)
            
            # Obtener la Persona
            persona = Persona.objects.get(rut=rut)
            
            # Determinar el rol - Verificar Especialista primero (tiene prioridad)
            rol = "desconocido"
            try:
                Especialista.objects.get(fk_rutp=persona)
                rol = "especialista"
            except Especialista.DoesNotExist:
                # Si no es especialista, verificar si es paciente
                try:
                    Paciente.objects.get(fk_rut=persona)
                    rol = "paciente"
                except Paciente.DoesNotExist:
                    pass
            
            # Guardar en sesión
            request.session['user_rut'] = persona.rut
            request.session['user_nombre'] = f"{persona.nombre} {persona.apellido}"
            request.session['user_rol'] = rol
            request.session.modified = True
            request.session.save()
            
            print(f"[DEBUG LOGIN] RUT: {rut}, ROL: {rol}, SESSION: {request.session.get('user_rol')}")
            
            return Response({
                'message': 'Login exitoso',
                'rol': rol,
                'user': {
                    'rut': persona.rut,
                    'nombre': persona.nombre,
                    'apellido': persona.apellido,
                    'correo': persona.correo
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Contraseña incorrecta'}, status=status.HTTP_400_BAD_REQUEST)
    
    except User.DoesNotExist:
        # Si no existe usuario Django, intenta con la contraseña hasheada en Persona
        try:
            persona = Persona.objects.get(rut=rut)
            if check_password(contrasena, persona.contrasena):
                # Guardar datos del usuario en la sesión
                request.session['user_rut'] = persona.rut
                request.session['user_nombre'] = f"{persona.nombre} {persona.apellido}"
                
                # Determinar rol - Verificar Especialista primero (tiene prioridad)
                rol = "desconocido"
                try:
                    Especialista.objects.get(fk_rutp=persona)
                    rol = "especialista"
                except Especialista.DoesNotExist:
                    # Si no es especialista, verificar si es paciente
                    try:
                        Paciente.objects.get(fk_rut=persona)
                        rol = "paciente"
                    except Paciente.DoesNotExist:
                        pass
                
                request.session['user_rol'] = rol
                request.session.modified = True
                request.session.save()
                
                print(f"[DEBUG LOGIN] RUT: {rut}, ROL: {rol}, SESSION: {request.session.get('user_rol')}")
                
                return Response({
                    'message': 'Login exitoso',
                    'rol': rol,
                    'user': {
                        'rut': persona.rut,
                        'nombre': persona.nombre,
                        'apellido': persona.apellido,
                        'correo': persona.correo
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Contraseña incorrecta'}, status=status.HTTP_400_BAD_REQUEST)
        except Persona.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    except Persona.DoesNotExist:
        return Response({'error': 'Persona no encontrada en base de datos'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([AllowAny])
def logout_view(request):
    # Limpiar datos específicos de la sesión
    request.session.pop('user_rut', None)
    request.session.pop('user_nombre', None)
    # Limpiar toda la sesión
    request.session.flush()
    logout(request)
    return redirect('index')

@api_view(['POST'])
@permission_classes([AllowAny])
def registro_view(request):
    serializer = RegistroSerializer(data=request.data)
    if serializer.is_valid():
        try:
            paciente = serializer.save()
            return Response({
                'message': 'Registro exitoso',
                'user': {
                    'rut': paciente.fk_rut.rut,
                    'nombre': paciente.fk_rut.nombre,
                    'apellido': paciente.fk_rut.apellido
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def debug_session(request):
    """Debug endpoint para ver la sesión actual"""
    return Response({
        'user_rut': request.session.get('user_rut'),
        'user_nombre': request.session.get('user_nombre'),
        'user_rol': request.session.get('user_rol'),
        'all_session': dict(request.session)
    })