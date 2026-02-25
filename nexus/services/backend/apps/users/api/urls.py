"""
apps/users/api/urls.py

URLs para endpoints de usuarios.

Rutas generadas por ViewSet:
- GET    /api/users/              → list
- POST   /api/users/              → create
- GET    /api/users/{id}/         → retrieve
- PUT    /api/users/{id}/         → update
- PATCH  /api/users/{id}/         → partial_update
- DELETE /api/users/{id}/         → destroy

Rutas custom:
- GET    /api/users/me/           → current_user
- POST   /api/users/{id}/change_password/ → change_password

Otras rutas:
- GET    /api/users/groups/       → list groups
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.users.api.views import UserViewSet, GroupListView

# Router para ViewSet (genera URLs automáticamente)
router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')

app_name = 'users'

urlpatterns = [
    
    # Additional endpoints
    path('groups/', GroupListView.as_view(), name='groups-list'),
    # ViewSet routes (CRUD + custom actions)
    path('', include(router.urls)),
]
