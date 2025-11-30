from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Drop all project tables'

    def handle(self, *args, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS seguimiento;")
            cursor.execute("DROP TABLE IF EXISTS consulta;")
            cursor.execute("DROP TABLE IF EXISTS especialista;")
            cursor.execute("DROP TABLE IF EXISTS paciente;")
            cursor.execute("DROP TABLE IF EXISTS persona;")
            self.stdout.write(self.style.SUCCESS('Successfully dropped all tables'))