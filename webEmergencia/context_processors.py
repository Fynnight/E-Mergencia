from .models import Persona, Paciente, Especialista


def user_role_context(request):
    user_role = None
    user_rut = request.session.get('user_rut')
    
    if user_rut:
        try:
            persona = Persona.objects.get(rut=user_rut)
            
            # Verificar Especialista primero (tiene prioridad)
            try:
                Especialista.objects.get(fk_rutp=persona)
                user_role = 'especialista'
                print(f"[CONTEXT PROCESSOR] RUT: {user_rut}, ENCONTRADO COMO ESPECIALISTA")
            except Especialista.DoesNotExist:
                # Si no es especialista, verificar si es paciente
                try:
                    Paciente.objects.get(fk_rut=persona)
                    user_role = 'paciente'
                    print(f"[CONTEXT PROCESSOR] RUT: {user_rut}, ENCONTRADO COMO PACIENTE")
                except Paciente.DoesNotExist:
                    user_role = 'desconocido'
                    print(f"[CONTEXT PROCESSOR] RUT: {user_rut}, ENCONTRADO COMO DESCONOCIDO")
        except Persona.DoesNotExist:
            print(f"[CONTEXT PROCESSOR] RUT: {user_rut}, PERSONA NO ENCONTRADA")
    else:
        print(f"[CONTEXT PROCESSOR] SIN user_rut EN SESION")
    
    print(f"[CONTEXT PROCESSOR] Retornando user_role: {user_role}")
    
    return {
        'user_role': user_role,
        'user_rut': user_rut,
    }
