"""
apps/core/urls.py

Health check endpoint para verificar que el servicio está funcionando.

Útil para:
- Docker health checks
- Kubernetes liveness/readiness probes
- Load balancers
- Monitoring (Datadog, New Relic, etc.)
"""
from django.urls import path
from apps.core.views import HealthCheckView

app_name = 'core'

urlpatterns = [
    path('', HealthCheckView.as_view(), name='health-check'),
]