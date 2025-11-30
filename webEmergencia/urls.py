from django.urls import path
from . import views
from . import auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('verificar-rut/', views.verificar_rut, name='verificar_rut'),
    path('registrar-y-agendar/', views.registrar_y_agendar, name='registrar_y_agendar'),
    path('agendar-nueva-cita/', views.agendar_nueva_cita, name='agendar_nueva_cita'),
    path('consultar-citas/', views.consultar_citas, name='consultar_citas'),
    path('modificar-cita/<int:cita_id>/', views.modificar_cita, name='modificar_cita'),
    path('eliminar-cita/<int:cita_id>/', views.eliminar_cita, name='eliminar_cita'),
    path('listar-consultas-medico/', views.listar_consultas_medico, name='listar_consultas_medico'),
    path('listar-pacientes/', views.listar_pacientes, name='listar_pacientes'),
    path('mis-documentos/', views.mis_documentos, name='mis_documentos'),
    
    # API URLs
    path('api/consultas/', views.consulta_list, name='consulta_list'),
    path('api/consultas/<int:pk>/', views.consulta_detail, name='consulta_detail'),
    path('api/consultas/<int:pk>/finalizar/', views.finalizar_consulta_view, name='finalizar_consulta'),
    path('api/citas-medico/<int:pk>/gestionar/', views.gestionar_cita_medico, name='gestionar_cita_medico'),
    path('api/paciente/<str:rut_paciente>/perfil/', views.ver_perfil_paciente, name='ver_perfil_paciente'),
    
    # Auth API URLs
    path('api/auth/login/', auth_views.login_view, name='api_login'),
    path('api/auth/logout/', auth_views.logout_view, name='api_logout'),
    path('api/auth/registro/', auth_views.registro_view, name='api_registro'),
    path('api/auth/debug-session/', auth_views.debug_session, name='debug_session'),
]