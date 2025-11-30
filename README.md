# E-mergencia - Sistema de Agendamiento de Citas Médicas Virtuales

## Instalar los requerimientos
```bash
pip install -r requirements.txt
```

## Hacer migraciones en caso de actualizacion
```bash
python manage.py migrate
```

## Runear
```bash
python manage.py runserver
```

## Vistas api
```bash
GET /api/consultas/: Lista todas las consultas
POST /api/consultas/: Crea una nueva consulta
GET /api/consultas/<id>/: Obtiene una consulta específica
PUT /api/consultas/<id>/: Actualiza una consulta específica
DELETE /api/consultas/<id>/: Elimina una consulta específica
```

## Configurar ALLOWED_HOST
```bash
Ir al cmd y buscar: "ipconfig"
Luego copiar la direccion IPv4 Adress
Agregar esta IP a settings.py en la parte de ALLOWED_HOST
Ejemplo:
ALLOWED_HOSTS = '127.0.0.1', 'localhost', '192.168.1.101'
Iniciar la app con la ip correcta: 
python manage.py runserver 0.0.0.0:8000
Por ultimo abrir la direccion en otro dispositivo:
http://IP:8000
En caso de no funcionar: 
Revisa el Firewall de tu computador por posible bloqueo del puerto :8000
python manage.py runsslserver 0.0.0.0:8000
```

## Cuenta de especialistas:
```bash
210903143
tam123456
987654321
Chopper123
```