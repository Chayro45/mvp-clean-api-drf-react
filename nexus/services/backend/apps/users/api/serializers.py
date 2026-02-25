"""
apps/users/api/serializers.py

Serializers para la API de usuarios.

¿Por qué separar serializers?
- Read vs Write: Diferentes campos en GET vs POST/PUT
- Security: No exponer password en responses
- Flexibilidad: Nested serializers para relaciones

Decisión técnica:
- UserSerializer: Para responses (GET) - incluye profile y permisos
- UserCreateSerializer: Para crear (POST) - incluye password
- UserUpdateSerializer: Para actualizar (PUT/PATCH) - sin password
"""
from rest_framework import serializers
from django.contrib.auth.models import User, Group
from apps.users.domain.models import UserProfile


class GroupSerializer(serializers.ModelSerializer):
    """
    Serializer simple para grupos (roles).
    
    Usado en nested serialization dentro de UserSerializer.
    """
    class Meta:
        model = Group
        fields = ['id', 'name']
        read_only_fields = ['id', 'name']


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer para UserProfile.
    
    Se usa nested dentro de UserSerializer.
    """
    full_name = serializers.CharField(read_only=True)
    roles = serializers.ListField(read_only=True)
    permissions_list = serializers.ListField(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'phone',
            'avatar_url',
            'department',
            'employee_id',
            'notes',
            'full_name',
            'roles',
            'permissions_list',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer principal para User (READ).
    
    Incluye:
    - Datos básicos del User
    - Profile nested
    - Grupos (roles)
    - Permisos
    
    Usado en:
    - GET /api/users/
    - GET /api/users/{id}/
    - GET /api/auth/me/
    """
    profile = UserProfileSerializer(read_only=True)
    groups = GroupSerializer(many=True, read_only=True)
    
    # Campos calculados
    full_name = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'is_active',
            'is_staff',
            'is_superuser',
            'date_joined',
            'last_login',
            'groups',
            'roles',
            'permissions',
            'profile',
        ]
        read_only_fields = [
            'id',
            'date_joined',
            'last_login',
        ]

    def get_full_name(self, obj):
        """Nombre completo del usuario"""
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username

    def get_roles(self, obj):
        """Lista de nombres de roles"""
        return [group.name for group in obj.groups.all()]

    def get_permissions(self, obj):
        """Lista de permisos (desde cache)"""
        from apps.core.permissions import get_user_permissions_cached
        return list(get_user_permissions_cached(obj))


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear usuarios (POST).
    
    Diferencias con UserSerializer:
    - Incluye password (write_only)
    - Permite asignar grupos
    - Incluye campos de profile
    
    Proceso:
    1. Valida datos
    2. Crea User con password hasheado
    3. Actualiza Profile (se crea automáticamente por signal)
    4. Asigna grupos
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        min_length=8,
        help_text="Mínimo 8 caracteres"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    # Campos de profile (opcionales)
    phone = serializers.CharField(required=False, allow_blank=True)
    avatar_url = serializers.URLField(required=False, allow_blank=True)
    department = serializers.CharField(required=False, allow_blank=True)
    employee_id = serializers.CharField(required=False, allow_blank=True)
    
    # Grupos (roles) - lista de IDs
    group_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True,
        help_text="Lista de IDs de grupos a asignar"
    )
    
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            'password_confirm',
            'first_name',
            'last_name',
            'is_active',
            'phone',
            'avatar_url',
            'department',
            'employee_id',
            'group_ids',
        ]

    def validate(self, data):
        """Validaciones custom"""
        # Verificar que passwords coincidan
        if data.get('password') != data.get('password_confirm'):
            raise serializers.ValidationError({
                'password_confirm': "Las contraseñas no coinciden"
            })
        
        # Remover password_confirm (no se guarda)
        data.pop('password_confirm', None)
        
        return data

    def create(self, validated_data):
        """
        Crea usuario con password hasheado y profile actualizado.
        
        Steps:
        1. Extraer campos de profile y grupos
        2. Crear User con create_user() (hashea password)
        3. Actualizar profile
        4. Asignar grupos
        """
        # Extraer campos que no son de User
        profile_data = {
            'phone': validated_data.pop('phone', None),
            'avatar_url': validated_data.pop('avatar_url', None),
            'department': validated_data.pop('department', None),
            'employee_id': validated_data.pop('employee_id', None),
        }
        group_ids = validated_data.pop('group_ids', [])
        
        # Extraer password
        password = validated_data.pop('password')
        
        # Crear usuario (password se hashea automáticamente)
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        
        # Actualizar profile (ya existe por signal)
        if any(profile_data.values()):
            for key, value in profile_data.items():
                if value:
                    setattr(user.profile, key, value)
            user.profile.save()
        
        # Asignar grupos
        if group_ids:
            user.groups.set(group_ids)
        
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para actualizar usuarios (PUT/PATCH).
    
    NO incluye password (se cambia por endpoint separado).
    Permite actualizar profile inline.
    """
    # Campos de profile
    phone = serializers.CharField(required=False, allow_blank=True)
    avatar_url = serializers.URLField(required=False, allow_blank=True)
    department = serializers.CharField(required=False, allow_blank=True)
    employee_id = serializers.CharField(required=False, allow_blank=True)
    
    # Grupos
    group_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True, 
        write_only=True
    )
    
    class Meta:
        model = User
        fields = [
            'email',
            'first_name',
            'last_name',
            'is_active',
            'phone',
            'avatar_url',
            'department',
            'employee_id',
            'group_ids',
        ]

    def update(self, instance, validated_data):
        """Actualiza User y Profile"""
        # Extraer campos de profile y grupos
        profile_data = {
            'phone': validated_data.pop('phone', None),
            'avatar_url': validated_data.pop('avatar_url', None),
            'department': validated_data.pop('department', None),
            'employee_id': validated_data.pop('employee_id', None),
        }
        group_ids = validated_data.pop('group_ids', None)
        
        # Actualizar User
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        
        # Actualizar Profile
        if any(profile_data.values()):
            for key, value in profile_data.items():
                if value is not None:
                    setattr(instance.profile, key, value)
            instance.profile.save()
        
        # Actualizar grupos
        if group_ids is not None:
            instance.groups.set(group_ids)
            # Invalidar cache de permisos
            from apps.core.permissions import invalidate_user_permissions_cache
            invalidate_user_permissions_cache(instance.id)
        
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer para cambiar password.
    
    Endpoint separado: POST /api/users/{id}/change_password/
    """
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, data):
        """Validar que passwords coincidan"""
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': "Las contraseñas no coinciden"
            })
        return data

    def validate_old_password(self, value):
        """Validar que el password actual sea correcto"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Password actual incorrecto")
        return value
