from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.http import JsonResponse
from .models import Persona, Paciente, Consulta, Especialista, Diagnostico, Receta
from .forms import VerificarRutForm, RegistroCompletoForm, CitaForm
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .serializers import ConsultaSerializer, DiagnosticoSerializer
import bcrypt
import requests
from django.db import transaction
from datetime import timedelta
from deep_translator import GoogleTranslator

# Helper function para determinar el rol del usuario
def get_user_role(request):
    """
    Determina el rol del usuario (paciente o medico) basado en la sesión.
    Retorna una tupla: (persona_obj, rol_obj, rol_string)
    Retorna (None, None, None) si no hay usuario autenticado o no existe el rol.
    """
    rut = request.session.get('user_rut')
    if not rut:
        return None, None, None
    
    try:
        persona = Persona.objects.get(rut=rut)
    except Persona.DoesNotExist:
        return None, None, None
    
    # Verificar si es especialista
    try:
        especialista = Especialista.objects.get(fk_rutp=persona)
        return persona, especialista, 'medico'
    except Especialista.DoesNotExist:
        pass
    
    # Verificar si es paciente
    try:
        paciente = Paciente.objects.get(fk_rut=persona)
        return persona, paciente, 'paciente'
    except Paciente.DoesNotExist:
        pass
    
    return None, None, None

def index(request):
    context = {}
    
    # Verificar si el usuario está logueado
    if 'user_rut' in request.session:
        rut = request.session.get('user_rut')
        try:
            # Obtener el objeto Persona
            persona = Persona.objects.get(rut=rut)
            context['persona'] = persona
            
            # Verificar si es Especialista
            es_especialista = Especialista.objects.filter(fk_rutp=persona).exists()
            context['es_especialista'] = es_especialista
        except Persona.DoesNotExist:
            # Si la persona no existe, limpiar sesión
            request.session.flush()
    
    return render(request, 'webEmergencia/index.html', context)

def verificar_rut(request):
    if request.method == 'POST':
        form = VerificarRutForm(request.POST)
        if form.is_valid():
            rut = form.cleaned_data['rut']
            try:
                persona = Persona.objects.get(rut=rut)
                request.session['rut'] = rut
                return redirect('agendar_nueva_cita')
            except Persona.DoesNotExist:
                request.session['rut'] = rut
                return redirect('registrar_y_agendar')
    else:
        form = VerificarRutForm()
    return render(request, 'webEmergencia/verificar_rut.html', {'form': form})

def registrar_y_agendar(request):
    rut = request.session.get('rut')
    if not rut:
        return redirect('verificar_rut')
    
    if request.method == 'POST':
        form = RegistroCompletoForm(request.POST)
        if form.is_valid():
            # Crear persona
            persona = form.save(commit=False)
            raw_password = get_random_string(12)
            hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt())
            persona.contrasena = hashed_password.decode('utf-8')
            persona.save()

            # Crear paciente
            paciente = Paciente.objects.create(
                fk_rut=persona,
                fecha_nacimiento=form.cleaned_data['fecha_nacimiento'],
                telefono=form.cleaned_data['telefono'],
                direccion=form.cleaned_data['direccion']
            )

            # Crear consulta
            Consulta.objects.create(
                fk_idpaciente=paciente,
                motivo=form.cleaned_data['motivo'],
                sintomas=form.cleaned_data['sintomas'],
                fecha_inicio=form.cleaned_data['fecha_inicio'],
                especialidad=form.cleaned_data['especialidad']
            )

            messages.success(request, 'Registro exitoso. Su cita ha sido agendada.')
            return redirect('index')
    else:
        form = RegistroCompletoForm(initial={'rut': rut})
    
    return render(request, 'webEmergencia/registrar_y_agendar.html', {'form': form})

def agendar_nueva_cita(request):
    rut = request.session.get('user_rut')
    if not rut:
        messages.error(request, 'Debe iniciar sesión para agendar una cita.')
        return redirect('index')
    
    try:
        persona = Persona.objects.get(rut=rut)
        paciente = Paciente.objects.get(fk_rut=persona)
    except (Persona.DoesNotExist, Paciente.DoesNotExist):
        messages.error(request, 'Error al obtener los datos del paciente.')
        return redirect('index')

    if request.method == 'POST':
        form = CitaForm(request.POST)
        if form.is_valid():
            consulta = form.save(commit=False)
            consulta.fk_idpaciente = paciente
            consulta.especialidad = form.cleaned_data['especialidad']
            consulta.save()
            
            messages.success(request, 'Cita agendada exitosamente.')
            return redirect('index')
    else:
        form = CitaForm()
    
    context = {
        'form': form,
        'persona': persona
    }
    return render(request, 'webEmergencia/agendar_nueva_cita.html', context)

def consultar_citas(request):
    rut = request.session.get('user_rut')
    if not rut:
        messages.error(request, 'Debe iniciar sesión para consultar sus citas.')
        return redirect('index')
    
    try:
        from django.utils import timezone
        persona = Persona.objects.get(rut=rut)
        paciente = Paciente.objects.get(fk_rut=persona)
        citas = Consulta.objects.filter(fk_idpaciente=paciente).order_by('-fecha_inicio')
        return render(request, 'webEmergencia/listar_citas.html', {
            'citas': citas,
            'persona': persona,
            'now': timezone.now()
        })
    except (Persona.DoesNotExist, Paciente.DoesNotExist):
        messages.error(request, 'Error al obtener los datos del paciente.')
        return redirect('index')

def modificar_cita(request, cita_id):
    cita = get_object_or_404(Consulta, id=cita_id)
    if request.method == 'POST':
        form = CitaForm(request.POST, instance=cita)
        if form.is_valid():
            consulta = form.save(commit=False)
            consulta.especialidad = form.cleaned_data['especialidad']
            consulta.save()
            
            messages.success(request, 'Cita modificada exitosamente.')
            return redirect('consultar_citas')
    else:
        form = CitaForm(instance=cita)
    
    return render(request, 'webEmergencia/modificar_cita.html', {'form': form, 'cita': cita})

def eliminar_cita(request, cita_id):
    cita = get_object_or_404(Consulta, id=cita_id)
    if request.method == 'POST':
        cita.delete()
        messages.success(request, 'Cita eliminada exitosamente.')
        return redirect('consultar_citas')
    
    return render(request, 'webEmergencia/eliminar_cita.html', {'cita': cita})

# API Views
@api_view(['GET', 'POST'])
def consulta_list(request):
    persona, rol_obj, rol_string = get_user_role(request)
    
    if not persona:
        return Response({'error': 'Usuario no autenticado'}, status=status.HTTP_401_UNAUTHORIZED)
    
    if request.method == 'GET':
        if rol_string == 'paciente':
            consultas = Consulta.objects.filter(fk_idpaciente=rol_obj).order_by('-fecha_inicio')
        elif rol_string == 'medico':
            consultas = Consulta.objects.all().order_by('-fecha_inicio')
            rut_paciente = request.query_params.get('rut_paciente')
            if rut_paciente:
                try:
                    persona_paciente = Persona.objects.get(rut=rut_paciente)
                    paciente = Paciente.objects.get(fk_rut=persona_paciente)
                    consultas = consultas.filter(fk_idpaciente=paciente)
                except (Persona.DoesNotExist, Paciente.DoesNotExist):
                    return Response({'error': 'Paciente no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'error': 'Rol no reconocido'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ConsultaSerializer(consultas, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Solo los pacientes pueden crear consultas
        if rol_string != 'paciente':
            return Response({'error': 'Solo los pacientes pueden crear consultas'}, status=status.HTTP_403_FORBIDDEN)
        
        # Añadir automáticamente el paciente a los datos
        data = request.data.copy()
        data['fk_idpaciente'] = rol_obj.id
        
        serializer = ConsultaSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def consulta_detail(request, pk):
    try:
        consulta = Consulta.objects.get(pk=pk)
    except Consulta.DoesNotExist:
        return Response({'error': 'Consulta no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    
    # Para GET, permitimos que pacientes vean sus propias consultas
    if request.method == 'GET':
        persona, rol_obj, rol_string = get_user_role(request)
        
        # Si es paciente, solo puede ver sus propias consultas
        if rol_string == 'paciente':
            if consulta.fk_idpaciente != rol_obj:
                return Response({'error': 'No tienes permiso para acceder a esta consulta'}, status=status.HTTP_403_FORBIDDEN)
        # Los médicos pueden ver cualquier consulta
        elif rol_string != 'medico':
            # Si no está autenticado, permitimos ver la consulta de todas formas
            pass
        
        serializer = ConsultaSerializer(consulta)
        return Response(serializer.data)
    
    # Para PUT y DELETE, se requiere autenticación
    persona, rol_obj, rol_string = get_user_role(request)
    
    if not persona:
        return Response({'error': 'Usuario no autenticado'}, status=status.HTTP_401_UNAUTHORIZED)

    # Verificar permisos según el rol
    if rol_string == 'paciente':
        # Un paciente solo puede modificar/eliminar sus propias consultas
        if consulta.fk_idpaciente != rol_obj:
            return Response({'error': 'No tienes permiso para acceder a esta consulta'}, status=status.HTTP_403_FORBIDDEN)
    elif rol_string != 'medico':
        return Response({'error': 'Rol no reconocido'}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'PUT':
        # Solo pacientes pueden modificar (y solo sus propias consultas)
        if rol_string != 'paciente':
            return Response({'error': 'Solo los pacientes pueden modificar consultas'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ConsultaSerializer(consulta, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Solo pacientes pueden eliminar (y solo sus propias consultas)
        if rol_string != 'paciente':
            return Response({'error': 'Solo los pacientes pueden eliminar consultas'}, status=status.HTTP_403_FORBIDDEN)
        
        consulta.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST', 'PUT'])
def gestionar_cita_medico(request, pk):
    """
    Vista para que los médicos gestionen citas (aceptar, cancelar, aplazar).
    """
    persona, rol_obj, rol_string = get_user_role(request)
    
    if not persona:
        return Response({'error': 'Usuario no autenticado'}, status=status.HTTP_401_UNAUTHORIZED)
    
    if rol_string != 'medico':
        return Response({'error': 'Solo los médicos pueden gestionar citas'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        consulta = Consulta.objects.get(pk=pk)
    except Consulta.DoesNotExist:
        return Response({'error': 'Consulta no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    
    accion = request.data.get('accion')
    
    if accion == 'aceptar':
        consulta.estado = 'aceptada'
        consulta.especialista_asignado = rol_obj
        consulta.save()
        serializer = ConsultaSerializer(consulta)
        return Response({'message': 'Cita aceptada', 'cita': serializer.data}, status=status.HTTP_200_OK)
    
    elif accion == 'cancelar':
        razon = request.data.get('razon')
        if not razon:
            return Response({'error': 'La razón de cancelación es requerida'}, status=status.HTTP_400_BAD_REQUEST)
        
        consulta.estado = 'cancelada'
        consulta.razon_cancelacion = razon
        consulta.save()
        serializer = ConsultaSerializer(consulta)
        return Response({'message': 'Cita cancelada', 'cita': serializer.data}, status=status.HTTP_200_OK)
    
    elif accion == 'aplazar':
        consulta.estado = 'aplazada'
        consulta.save()
        serializer = ConsultaSerializer(consulta)
        return Response({'message': 'Cita aplazada', 'cita': serializer.data}, status=status.HTTP_200_OK)
    
    else:
        return Response({'error': 'Acción no reconocida. Use: aceptar, cancelar o aplazar'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def ver_perfil_paciente(request, rut_paciente):
    """
    Vista para que los médicos vean el perfil de un paciente.
    Solo los médicos pueden acceder a esta vista.
    """
    persona, rol_obj, rol_string = get_user_role(request)
    
    if not persona:
        return Response({'error': 'Usuario no autenticado'}, status=status.HTTP_401_UNAUTHORIZED)
    
    if rol_string != 'medico':
        return Response({'error': 'Solo los médicos pueden ver perfiles de pacientes'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        persona_paciente = Persona.objects.get(rut=rut_paciente)
        paciente = Paciente.objects.get(fk_rut=persona_paciente)
    except (Persona.DoesNotExist, Paciente.DoesNotExist):
        return Response({'error': 'Paciente no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    # Obtener citas del paciente
    citas = Consulta.objects.filter(fk_idpaciente=paciente).order_by('-fecha_inicio')
    
    data = {
        'persona': {
            'rut': persona_paciente.rut,
            'nombre': persona_paciente.nombre,
            'apellido': persona_paciente.apellido,
            'correo': persona_paciente.correo
        },
        'paciente': {
            'id': paciente.id,
            'fecha_nacimiento': paciente.fecha_nacimiento,
            'telefono': paciente.telefono,
            'direccion': paciente.direccion
        },
        'citas': ConsultaSerializer(citas, many=True).data
    }
    
    return Response(data, status=status.HTTP_200_OK)

def listar_consultas_medico(request):
    """
    Vista para que los médicos vean todas las consultas de todos los pacientes.
    Permite filtrar por RUT del paciente.
    """
    persona, rol_obj, rol_string = get_user_role(request)
    
    if not persona:
        return redirect('index')
    
    if rol_string != 'medico':
        return redirect('index')
    
    # Obtener todas las consultas
    consultas = Consulta.objects.all().order_by('-fecha_inicio')
    
    # Filtrar por RUT si se proporciona
    rut_filtro = request.GET.get('rut', '')
    if rut_filtro:
        consultas = consultas.filter(fk_idpaciente__fk_rut__rut=rut_filtro)
    
    # Preparar datos para mostrar
    consultas_data = []
    for consulta in consultas:
        consultas_data.append({
            'id': consulta.id,
            'paciente_rut': consulta.fk_idpaciente.fk_rut.rut,
            'paciente_nombre': f"{consulta.fk_idpaciente.fk_rut.nombre} {consulta.fk_idpaciente.fk_rut.apellido}",
            'fecha_inicio': consulta.fecha_inicio,
            'especialidad': consulta.especialidad,
            'estado': consulta.estado,
            'motivo': consulta.motivo,
            'sintomas': consulta.sintomas
        })
    
    context = {
        'consultas': consultas_data,
        'rut_filtro': rut_filtro
    }
    
    return render(request, 'webEmergencia/listar_consultas_medico.html', context)

def listar_pacientes(request):
    """
    Vista para que los médicos vean todos los pacientes registrados.
    """
    persona, rol_obj, rol_string = get_user_role(request)
    
    if not persona:
        return redirect('index')
    
    if rol_string != 'medico':
        return redirect('index')
    
    # Obtener todos los pacientes
    pacientes = Paciente.objects.all().order_by('fk_rut__apellido', 'fk_rut__nombre')
    
    # Preparar datos para mostrar
    pacientes_data = []
    for paciente in pacientes:
        persona_data = paciente.fk_rut
        # Contar consultas del paciente
        num_consultas = Consulta.objects.filter(fk_idpaciente=paciente).count()
        
        pacientes_data.append({
            'id': paciente.id,
            'rut': persona_data.rut,
            'nombre': persona_data.nombre,
            'apellido': persona_data.apellido,
            'correo': persona_data.correo,
            'telefono': paciente.telefono,
            'direccion': paciente.direccion,
            'fecha_nacimiento': paciente.fecha_nacimiento,
            'num_consultas': num_consultas
        })
    
    context = {
        'pacientes': pacientes_data
    }
    
    return render(request, 'webEmergencia/listar_pacientes.html', context)

def mis_documentos(request):
    """
    Vista para que los pacientes vean todos sus diagnósticos.
    Ordena por fecha de la consulta médica.
    """
    rut = request.session.get('user_rut')
    if not rut:
        messages.error(request, 'Debe iniciar sesión para ver sus documentos.')
        return redirect('index')
    
    try:
        persona = Persona.objects.get(rut=rut)
        paciente = Paciente.objects.get(fk_rut=persona)
    except (Persona.DoesNotExist, Paciente.DoesNotExist):
        messages.error(request, 'Error al obtener los datos del paciente.')
        return redirect('index')
    
    # Obtener todas las consultas finalizadas del paciente con diagnóstico
    consultas_finalizadas = Consulta.objects.filter(
        fk_idpaciente=paciente,
        estado='finalizada',
        diagnostico_data__isnull=False
    ).order_by('-fecha_inicio').select_related('diagnostico_data')
    
    # Preparar datos con diagnósticos y recetas
    documentos = []
    for consulta in consultas_finalizadas:
        if hasattr(consulta, 'diagnostico_data'):
            diagnostico = consulta.diagnostico_data
            documentos.append({
                'consulta_id': consulta.id,
                'consulta_fecha': consulta.fecha_inicio,
                'consulta_motivo': consulta.motivo,
                'consulta_especialidad': consulta.especialidad,
                'diagnostico': diagnostico,
                'recetas': diagnostico.recetas.all()
            })
    
    context = {
        'persona': persona,
        'documentos': documentos,
        'num_documentos': len(documentos)
    }
    
    return render(request, 'webEmergencia/mis_documentos.html', context)

@api_view(['POST'])
def finalizar_consulta_view(request, pk):
    """
    Vista para que los especialistas finalicen una consulta.
    Crea Diagnostico, Recetas y, si es crónico, crea automáticamente una consulta de seguimiento.
    
    Estructura esperada del JSON:
    {
        "descripcion": "Descripción del diagnóstico",
        "es_cronico": true,
        "nombre_enfermedad": "Diabetes",
        "recetas": [
            {"medicamento": "Paracetamol", "dosis": "500mg", "horario": "Cada 8 horas por 3 días"},
            {"medicamento": "Ibuprofen", "dosis": "400mg", "horario": "Cada 6 horas por 5 días"}
        ]
    }
    """
    # 1. Validaciones: Obtener usuario desde request.session['rut']
    rut = request.session.get('user_rut')
    if not rut:
        return Response({'error': 'Usuario no autenticado'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        persona_especialista = Persona.objects.get(rut=rut)
        especialista = Especialista.objects.get(fk_rutp=persona_especialista)
    except (Persona.DoesNotExist, Especialista.DoesNotExist):
        return Response({'error': 'Solo especialistas pueden finalizar consultas'}, status=status.HTTP_403_FORBIDDEN)
    
    # 2. Obtener la consulta por pk
    try:
        consulta = Consulta.objects.get(pk=pk)
    except Consulta.DoesNotExist:
        return Response({'error': 'Consulta no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    
    # 3. Verificar que pertenezca a ese especialista
    if consulta.especialista_asignado != especialista:
        return Response({'error': 'No tienes permiso para finalizar esta consulta'}, status=status.HTTP_403_FORBIDDEN)
    
    # 4. Verificar que el estado actual sea 'aceptada'
    if consulta.estado != 'aceptada':
        return Response({'error': f'La consulta debe estar en estado "aceptada", estado actual: {consulta.estado}'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Usar transaction.atomic para garantizar integridad
    try:
        with transaction.atomic():
            # A. Crear Diagnostico
            descripcion = request.data.get('descripcion')
            es_cronico = request.data.get('es_cronico', False)
            nombre_enfermedad = request.data.get('nombre_enfermedad', None)
            
            if not descripcion:
                return Response({'error': 'La descripción del diagnóstico es requerida'}, status=status.HTTP_400_BAD_REQUEST)
            
            diagnostico = Diagnostico.objects.create(
                consulta=consulta,
                descripcion=descripcion,
                es_cronico=es_cronico,
                nombre_enfermedad=nombre_enfermedad if es_cronico else None
            )
            
            # B. Crear Recetas (Lista)
            recetas_data = request.data.get('recetas', [])
            if not isinstance(recetas_data, list):
                return Response({'error': 'Las recetas deben ser una lista'}, status=status.HTTP_400_BAD_REQUEST)
            
            for receta_item in recetas_data:
                medicamento = receta_item.get('medicamento')
                dosis = receta_item.get('dosis')
                horario = receta_item.get('horario')
                
                if not all([medicamento, dosis, horario]):
                    return Response({'error': 'Cada receta debe tener medicamento, dosis y horario'}, status=status.HTTP_400_BAD_REQUEST)
                
                Receta.objects.create(
                    diagnostico=diagnostico,
                    medicamento=medicamento,
                    dosis=dosis,
                    horario=horario
                )
            
            # C. Lógica Crónico (Automática)
            if es_cronico and nombre_enfermedad:
                # Calcular nueva fecha: Sumar 7 días a la fecha de la consulta actual
                fecha_seguimiento = consulta.fecha_inicio + timedelta(days=7)
                
                # Crear nueva Consulta de seguimiento
                Consulta.objects.create(
                    fk_idpaciente=consulta.fk_idpaciente,
                    fk_idespecialista=consulta.fk_idespecialista,
                    especialista_asignado=especialista,
                    motivo=f"Control Crónico: {nombre_enfermedad}",
                    especialidad=consulta.especialidad,
                    fecha_inicio=fecha_seguimiento,
                    estado='aceptada'
                )
            
            # D. Cambiar estado de consulta original a 'finalizada'
            consulta.estado = 'finalizada'
            consulta.save()
            
            # E. Retornar respuesta 200 OK con datos
            serializer = ConsultaSerializer(consulta)
            return Response({
                'message': 'Consulta finalizada exitosamente',
                'cita': serializer.data,
                'diagnostico': DiagnosticoSerializer(diagnostico).data
            }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'error': f'Error al finalizar la consulta: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def buscar_medicamentos_api(request):
    query = request.GET.get('q', '')
    
    if not query or len(query) < 3:
        return JsonResponse([], safe=False)

    try:
        # 1. TRADUCIR LA BÚSQUEDA (Español -> Inglés)
        # Esto permite buscar "Acido" y que la API entienda "Acid"
        translator_es_en = GoogleTranslator(source='es', target='en')
        query_en = translator_es_en.translate(query)
        
        # 2. CONSULTAR A OPENFDA (En inglés)
        url = f"https://api.fda.gov/drug/label.json?search=openfda.brand_name:{query_en}*&limit=5"
        response = requests.get(url)
        data = response.json()
        
        resultados_en = []
        if 'results' in data:
            for item in data['results']:
                if 'openfda' in item and 'brand_name' in item['openfda']:
                    # Guardamos el nombre en inglés temporalmente
                    brand_name = item['openfda']['brand_name'][0]
                    resultados_en.append(brand_name)
        
        # 3. TRADUCIR RESULTADOS DE VUELTA (Inglés -> Español)
        # Si hay resultados, los traducimos todos juntos para que sea rápido
        resultados_es = []
        if resultados_en:
            translator_en_es = GoogleTranslator(source='en', target='es')
            # translate_batch toma una lista y devuelve una lista traducida
            resultados_es = translator_en_es.translate_batch(resultados_en)

        # 4. DEVOLVER LA LISTA EN ESPAÑOL
        return JsonResponse(resultados_es, safe=False)

    except Exception as e:
        print(f"Error en API o Traducción: {e}")
        # En caso de error, devolvemos una lista vacía para no romper el frontend
        return JsonResponse([], safe=False)