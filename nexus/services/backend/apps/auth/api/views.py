"""
apps/auth/api/views.py

Views para autenticación JWT.

Endpoints:
- POST /api/auth/login/     → Login con username/password
- POST /api/auth/refresh/   → Refrescar access token
- POST /api/auth/logout/    → Logout (blacklist refresh token)
- POST /api/auth/verify/    → Verificar token

Flujo típico:
1. Login → Obtiene access + refresh token
2. Cada request → Usa access token en header: Authorization: Bearer {token}
3. Access expira → Usa refresh token para obtener nuevo access
4. Refresh expira → Re-login
5. Logout → Blacklist refresh token
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone

from apps.auth.api.serializers import (
    LoginSerializer,
    TokenRefreshSerializer,
    LogoutSerializer,
    VerifyTokenSerializer
)
from rest_framework.throttling import UserRateThrottle

class LoginRateThrottle(UserRateThrottle):
    rate = '5/minute'

class LoginView(APIView):
    throttle_classes = [LoginRateThrottle]
    """
    Login con username/password.
    
    POST /api/auth/login/
    
    Request:
        {
            "username": "admin",
            "password": "admin123"
        }
    
    Response (200):
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
    
    Response (400):
        {
            "detail": "Credenciales inválidas"
        }
    """
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        """Procesa login"""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Serializer ya generó tokens y user data
        data = serializer.validated_data
        
        # Actualizar last_login (Django no lo hace automáticamente con JWT)
        user = request.data.get('username')
        from django.contrib.auth.models import User
        user_obj = User.objects.get(username=user)
        user_obj.last_login = timezone.now()
        user_obj.save(update_fields=['last_login'])
        
        return Response(data, status=status.HTTP_200_OK)


class TokenRefreshView(APIView):
    """
    Refresca access token usando refresh token.
    
    POST /api/auth/refresh/
    
    Request:
        {
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
        }
    
    Response (200):
        {
            "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
        }
    
    Response (400):
        {
            "detail": "Token inválido: ..."
        }
    
    ¿Cuándo llamar esto?
    - Cuando API retorna 401 Unauthorized
    - Proactivamente antes de que access expire (opcional)
    - Frontend puede verificar exp del token y refrescar antes
    """
    permission_classes = [AllowAny]
    serializer_class = TokenRefreshSerializer

    def post(self, request):
        """Procesa refresh"""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        return Response(
            serializer.validated_data,
            status=status.HTTP_200_OK
        )


class LogoutView(APIView):
    """
    Logout (blacklist refresh token).
    
    POST /api/auth/logout/
    
    Request:
        {
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
        }
    
    Response (200):
        {
            "detail": "Logout exitoso"
        }
    
    IMPORTANTE: 
    - Requiere simplejwt.token_blacklist en INSTALLED_APPS
    - Crear tabla de blacklist: python manage.py migrate
    - Access token sigue válido hasta expirar (mantener TTL corto)
    
    Frontend debe:
    1. Llamar a este endpoint
    2. Eliminar tokens del localStorage/sessionStorage
    3. Redirect a login
    """
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request):
        """Procesa logout"""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        return Response(
            serializer.validated_data,
            status=status.HTTP_200_OK
        )


class VerifyTokenView(APIView):
    """
    Verifica validez de access token.
    
    POST /api/auth/verify/
    
    Request:
        {
            "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
        }
    
    Response (200):
        {
            "valid": true,
            "user_id": 1,
            "exp": 1234567890
        }
    
    Response (400):
        {
            "detail": "Token inválido: ..."
        }
    
    Uso típico:
    - Frontend verifica token al cargar app
    - Si inválido → auto-refresh o redirect a login
    """
    permission_classes = [AllowAny]
    serializer_class = VerifyTokenSerializer

    def post(self, request):
        """Verifica token"""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        return Response(
            serializer.validated_data,
            status=status.HTTP_200_OK
        )


class CurrentUserView(APIView):
    """
    Retorna info del usuario autenticado.
    
    GET /api/auth/me/
    
    Headers:
        Authorization: Bearer {access_token}
    
    Response:
        {
            "id": 1,
            "username": "admin",
            "email": "admin@example.com",
            "full_name": "Admin User",
            "roles": ["Administrador"],
            "permissions": ["users.view_user", ...],
            "profile": {...}
        }
    
    Útil para:
    - Frontend obtiene info del usuario al cargar
    - Verificar permisos para mostrar/ocultar UI
    - Mostrar perfil en navbar
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retorna usuario actual"""
        from apps.users.api.serializers import UserSerializer
        
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
