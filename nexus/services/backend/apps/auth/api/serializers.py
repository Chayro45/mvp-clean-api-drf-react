"""
apps/auth/api/serializers.py

Serializers para autenticación JWT.

Stack de autenticación:
- SimpleJWT: Manejo de tokens
- Django Auth: Verificación de usuario/password
- Custom Login: Incluir info extra en response

¿Por qué JWT?
- Stateless: No requiere sesión en servidor
- Portable: Funciona entre servicios
- Frontend-friendly: Fácil de usar en React/Vue/etc.
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User


class LoginSerializer(serializers.Serializer):
    """
    Serializer para login con username/password.
    
    Process:
    1. Validar username y password
    2. Autenticar con Django auth
    3. Generar tokens JWT
    4. Retornar tokens + user info
    
    Request:
        POST /api/auth/login/
        {
            "username": "admin",
            "password": "admin123"
        }
    
    Response:
        {
            "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
            "user": {
                "id": 1,
                "username": "admin",
                "email": "admin@example.com",
                "full_name": "Admin User",
                "roles": ["Administrador"],
                "permissions": ["users.view_user", ...]
            }
        }
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        """
        Valida credenciales y genera tokens.
        
        Returns:
            dict: Incluye access, refresh y user
        
        Raises:
            ValidationError: Si credenciales inválidas
        """
        username = attrs.get('username')
        password = attrs.get('password')

        # Autenticar con Django
        user = authenticate(username=username, password=password)

        if user is None:
            raise serializers.ValidationError(
                'Credenciales inválidas',
                code='invalid_credentials'
            )

        if not user.is_active:
            raise serializers.ValidationError(
                'Usuario inactivo',
                code='inactive_user'
            )

        # Generar tokens JWT
        refresh = RefreshToken.for_user(user)

        # Preparar data de usuario
        from apps.users.api.serializers import UserSerializer
        user_data = UserSerializer(user).data

        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': user_data,
        }


class TokenRefreshSerializer(serializers.Serializer):
    """
    Serializer para refrescar access token.
    
    ¿Cuándo usar esto?
    - Access token expiró (típicamente 15-60 min)
    - Refresh token aún válido (típicamente 1-7 días)
    - Evita re-login del usuario
    
    Request:
        POST /api/auth/refresh/
        {
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
        }
    
    Response:
        {
            "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."  # Nuevo access token
        }
    """
    refresh = serializers.CharField(required=True)

    def validate(self, attrs):
        """Valida refresh token y genera nuevo access token"""
        from rest_framework_simplejwt.tokens import RefreshToken
        from rest_framework_simplejwt.exceptions import TokenError

        refresh_token = attrs.get('refresh')

        try:
            # Validar y refrescar
            refresh = RefreshToken(refresh_token)
            access = str(refresh.access_token)

            return {
                'access': access,
            }

        except TokenError as e:
            raise serializers.ValidationError(
                f'Token inválido: {str(e)}',
                code='invalid_token'
            )


class LogoutSerializer(serializers.Serializer):
    """
    Serializer para logout (blacklist de refresh token).
    
    ¿Cómo funciona JWT logout?
    - JWT es stateless, no hay "sesión" que cerrar
    - Solución: Blacklist del refresh token
    - Access token sigue válido hasta expirar (corto TTL)
    
    Request:
        POST /api/auth/logout/
        {
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
        }
    
    Response:
        {
            "detail": "Logout exitoso"
        }
    
    NOTA: Requiere simplejwt.token_blacklist en INSTALLED_APPS
    """
    refresh = serializers.CharField(required=True)

    def validate(self, attrs):
        """Blacklist el refresh token"""
        from rest_framework_simplejwt.tokens import RefreshToken
        from rest_framework_simplejwt.exceptions import TokenError

        refresh_token = attrs.get('refresh')

        try:
            # Blacklist el token
            token = RefreshToken(refresh_token)
            token.blacklist()

            return {'detail': 'Logout exitoso'}

        except TokenError as e:
            raise serializers.ValidationError(
                f'Token inválido: {str(e)}',
                code='invalid_token'
            )
        except AttributeError:
            # Si token_blacklist no está instalado
            raise serializers.ValidationError(
                'Blacklist no configurado. Agrega rest_framework_simplejwt.token_blacklist a INSTALLED_APPS',
                code='blacklist_not_enabled'
            )


class VerifyTokenSerializer(serializers.Serializer):
    """
    Serializer para verificar validez de access token.
    
    Útil para:
    - Frontend verifica si debe refrescar token
    - Middleware de otros servicios
    
    Request:
        POST /api/auth/verify/
        {
            "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
        }
    
    Response (si válido):
        {
            "valid": true,
            "user_id": 1,
            "username": "admin",
            "exp": 1234567890  # Unix timestamp de expiración
        }
    
    Response (si inválido):
        400 Bad Request
    """
    token = serializers.CharField(required=True)

    def validate(self, attrs):
        """Verifica y decodifica token"""
        from rest_framework_simplejwt.tokens import AccessToken
        from rest_framework_simplejwt.exceptions import TokenError

        token = attrs.get('token')

        try:
            # Decodificar y validar
            access_token = AccessToken(token)

            return {
                'valid': True,
                'user_id': access_token['user_id'],
                'exp': access_token['exp'],
            }

        except TokenError as e:
            raise serializers.ValidationError(
                f'Token inválido: {str(e)}',
                code='invalid_token'
            )
