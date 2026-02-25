"""
apps/core/management/commands/wait_for_db.py

Management command para esperar a que la base de datos esté lista.

¿Por qué esto?
- Docker Compose inicia servicios en paralelo
- Backend puede iniciar antes que PostgreSQL esté listo
- Este comando espera a que DB acepte conexiones
- Evita errores de "database not ready" en startup

Ejecutar:
    python manage.py wait_for_db

Uso en docker-compose:
    command: >
      sh -c "
        python manage.py wait_for_db &&
        python manage.py migrate &&
        ...
      "
"""
import time
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    help = 'Espera a que la base de datos esté disponible'

    def handle(self, *args, **options):
        self.stdout.write('⏳ Esperando base de datos...')
        
        db_conn = None
        max_retries = 30  # Máximo 30 segundos
        retry_delay = 1  # 1 segundo entre intentos
        
        for attempt in range(1, max_retries + 1):
            try:
                # Intentar conectar a la base de datos
                db_conn = connections['default']
                db_conn.cursor()
                
                # Si llegamos aquí, la conexión fue exitosa
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Base de datos lista (intento {attempt})')
                )
                return
                
            except OperationalError as e:
                # Base de datos no está lista aún
                self.stdout.write(
                    self.style.WARNING(
                        f'  → Intento {attempt}/{max_retries}: Base de datos no disponible'
                    )
                )
                
                if attempt == max_retries:
                    # Último intento fallido
                    self.stdout.write(
                        self.style.ERROR(
                            f'✗ Base de datos no disponible después de {max_retries} intentos'
                        )
                    )
                    self.stdout.write(
                        self.style.ERROR(f'Error: {str(e)}')
                    )
                    raise e
                
                # Esperar antes del siguiente intento
                time.sleep(retry_delay)
        
        # Esto no debería alcanzarse, pero por si acaso
        self.stdout.write(
            self.style.ERROR('✗ Error inesperado esperando base de datos')
        )