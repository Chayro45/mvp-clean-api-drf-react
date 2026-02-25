"""
apps/users/api/views.py

ViewSet para CRUD de usuarios.

¿Por qué ViewSet vs APIView?
- Menos código: CRUD automático
- Routers: URLs automáticas
- Actions custom: Fácil agregar endpoints extra
- Consistente: Patrón standard de DRF

Permisos por acción:
- list: users.view_user
- retrieve: users.view_user
- create: users.add_user
- update/partial_update: users.change_user
- destroy: users.delete_user
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User

from apps.core.permissions import HasPermission
from apps.users.api.serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer
)
from apps.users.application.services import UserService

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from django_filters import rest_framework as filters

class UserFilter(filters.FilterSet):
    username = filters.CharFilter(lookup_expr='icontains')
    email = filters.CharFilter(lookup_expr='icontains')
    is_active = filters.BooleanFilter()
    created_after = filters.DateTimeFilter(field_name='date_joined', lookup_expr='gte')
    
    class Meta:
        model = User
        fields = ['username', 'email', 'is_active', 'is_staff']

class UserViewSet(viewsets.ModelViewSet):
    filterset_class = UserFilter
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'date_joined', 'last_login']
    ordering = ['-date_joined']
    """
    ViewSet para gestión de usuarios.
    
    Endpoints generados automáticamente:
    - GET    /api/users/          → list()
    - POST   /api/users/          → create()
    - GET    /api/users/{id}/     → retrieve()
    - PUT    /api/users/{id}/     → update()
    - PATCH  /api/users/{id}/     → partial_update()
    - DELETE /api/users/{id}/     → destroy()
    
    Endpoints custom (actions):
    - GET    /api/users/me/       → current_user()
    - POST   /api/users/{id}/change_password/  → change_password()
    """
    @extend_schema(
            summary="Listar usuarios",
            description="Retorna lista paginada de usuarios del sistema",
            tags=['users'],
        )
    def list(self, request, *args, **kwargs):
            return super().list(request, *args, **kwargs)
        
    @extend_schema(
        summary="Crear usuario",
        description="Crea un nuevo usuario en el sistema",
        tags=['users'],
        examples=[
            OpenApiExample(
                'Ejemplo válido',
                value={
                    "username": "newuser",
                    "email": "user@example.com",
                    "password": "securepass123",
                    "password_confirm": "securepass123",
                    "first_name": "John",
                    "last_name": "Doe"
                }
            )
        ]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    queryset = User.objects.select_related('profile').prefetch_related('groups').all()
    permission_classes = [IsAuthenticated, HasPermission]
    
    # Permisos requeridos por acción
    required_permissions = {
        'list': ['auth.view_user'],
        'retrieve': ['auth.view_user'],
        'create': ['auth.add_user'],
        'update': ['auth.change_user'],
        'partial_update': ['auth.change_user'],
        'destroy': ['auth.delete_user'],
        'me': [],  # Solo autenticación
        'change_password': [],  # Propio usuario o admin
    }
    
    def get_queryset(self):
        """
        Filtrar queryset según permisos.
        
        - Superuser: Ve todos
        - Staff con permiso: Ve todos
        - Usuario normal: Solo se ve a sí mismo
        """
        user = self.request.user
        
        if user.is_superuser:
            return self.queryset
        
        # Si tiene permiso view_user, ve todos
        from apps.core.permissions import has_permission
        if has_permission(user, 'auth.view_user'):
            return self.queryset
        
        # Solo ve su propio usuario
        return self.queryset.filter(id=user.id)

    def get_serializer_class(self):
        """
        Retorna el serializer según la acción.
        
        ¿Por qué diferentes serializers?
        - create: Necesita password
        - update: No debe cambiar password
        - retrieve/list: Solo lectura con info completa
        """
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer

    def create(self, request, *args, **kwargs):
        """
        Crea un nuevo usuario.
        
        Delega la lógica de negocio al service.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Crear a través del service
        service = UserService(user=request.user)
        user = service.create_user(serializer.validated_data)
        
        # El serializer crea el usuario
        user = serializer.save() 

        # Retornar con serializer de lectura
        output_serializer = UserSerializer(user)
        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED
        )
    def partial_update(self, request, *args, **kwargs):
        """Actualización parcial de usuario"""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    def update(self, request, *args, **kwargs):
        """Actualiza un usuario existente"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # Actualizar a través del service
        service = UserService(user=request.user)
        service.update_user(instance, serializer.validated_data)
        
        # El serializer actualiza el usuario
        user = serializer.save()
        
        output_serializer = UserSerializer(user)
        return Response(output_serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Soft delete de usuario.
        
        NO borra de DB, solo marca como inactivo y soft-deleted el profile.
        """
        instance = self.get_object()
        
        service = UserService(user=request.user)
        service.delete_user(instance)
        
        return Response(
            {'detail': 'Usuario eliminado correctamente'},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        Retorna el usuario actual autenticado.
        
        GET /api/users/me/
        
        Útil para:
        - Frontend obtener info del usuario logueado
        - Verificar permisos y roles
        - Mostrar perfil
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def change_password(self, request, pk=None):
        """
        Cambia el password de un usuario.
        
        POST /api/users/{id}/change_password/
        
        Body:
        {
            "old_password": "...",
            "new_password": "...",
            "new_password_confirm": "..."
        }
        
        Reglas:
        - Cualquier usuario puede cambiar su propio password
        - Admin puede cambiar password de otros (sin old_password)
        """
        user = self.get_object()
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        # Verificar permisos
        is_own_password = user.id == request.user.id
        is_admin = request.user.is_superuser or has_permission(
            request.user, 'auth.change_user'
        )
        
        if not is_own_password and not is_admin:
            return Response(
                {'detail': 'No tienes permiso para cambiar este password'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Si es admin cambiando password de otro, no requiere old_password
        if not is_own_password and is_admin:
            user.set_password(serializer.validated_data['new_password'])
            user.save()
        else:
            # Cambio de propio password (ya validado old_password en serializer)
            user.set_password(serializer.validated_data['new_password'])
            user.save()
        
        return Response({
            'detail': 'Password cambiado correctamente'
        })


# Vista adicional: Lista de grupos disponibles
from rest_framework.views import APIView
from django.contrib.auth.models import Group
from apps.users.api.serializers import GroupSerializer


class GroupListView(APIView):
    """
    Lista de grupos (roles) disponibles.
    
    GET /api/users/groups/
    
    Usado para:
    - Dropdown al crear/editar usuario
    - Mostrar roles disponibles
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Lista todos los grupos"""
        groups = Group.objects.all()
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data)
