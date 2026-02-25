"""
apps/core/views.py

Vistas compartidas del core.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.db import connection
from django.core.cache import cache


class HealthCheckView(APIView):
    """
    Health check endpoint.
    
    GET /health/
    
    Verifica:
    - Que el servicio esté up
    - Conexión a base de datos
    - Conexión a Redis (cache)
    
    Response (200 OK):
    {
        "status": "healthy",
        "database": "connected",
        "cache": "connected"
    }
    
    Response (503 Service Unavailable):
    {
        "status": "unhealthy",
        "database": "error: ...",
        "cache": "error: ..."
    }
    
    Uso en Docker:
    --------------
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
      interval: 30s
      timeout: 10s
      retries: 3
    """
    permission_classes = [AllowAny]  # No requiere autenticación
    
    def get(self, request):
        """Health check"""
        health_status = {
            'status': 'healthy',
            'database': 'unknown',
            'cache': 'unknown',
        }
        
        # Check database
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            health_status['database'] = 'connected'
        except Exception as e:
            health_status['status'] = 'unhealthy'
            health_status['database'] = f'error: {str(e)}'
        
        # Check cache (Redis)
        try:
            cache.set('health_check', 'ok', timeout=10)
            if cache.get('health_check') == 'ok':
                health_status['cache'] = 'connected'
            else:
                health_status['cache'] = 'error: cache not working'
                health_status['status'] = 'unhealthy'
        except Exception as e:
            health_status['status'] = 'unhealthy'
            health_status['cache'] = f'error: {str(e)}'
        
        # Determinar status code
        status_code = (
            status.HTTP_200_OK 
            if health_status['status'] == 'healthy' 
            else status.HTTP_503_SERVICE_UNAVAILABLE
        )
        
        return Response(health_status, status=status_code)