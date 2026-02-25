"""
apps/auth/application/services.py

Service layer para autenticación.

¿Por qué service para auth si el serializer ya hace todo?
- Centralizar lógica de negocio (logging, rate limiting, etc.)
- Facilitar testing
- Futuro: Agregar MFA, OAuth, etc. sin tocar serializers

Por ahora es simple, pero preparado para crecer.
"""
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed, ValidationError
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """
    Service para gestión de autenticación.
    
    Centraliza:
    - Login con credenciales
    - Generación de tokens
    - Refresh de tokens
    - Logout (blacklist)
    - Auditoría de login/logout
    """

    @staticmethod
    def login(username: str, password: str) -> dict:
        """
        Autenticar usuario y generar tokens.
        
        Args:
            username: Nombre de usuario
            password: Contraseña
        
        Returns:
            dict: {
                'access': str,
                'refresh': str,
                'user': User object
            }
        
        Raises:
            AuthenticationFailed: Si credenciales inválidas
        
        Lógica adicional:
        - Log de intento de login
        - Actualizar last_login
        - TODO: Rate limiting (prevenir brute force)
        - TODO: Log de IP, user agent
        """
        # Log intento
        logger.info(f"Login attempt for username: {username}")
        
        # Autenticar
        user = authenticate(username=username, password=password)
        
        if user is None:
            logger.warning(f"Failed login attempt for username: {username}")
            raise AuthenticationFailed('Credenciales inválidas')
        
        if not user.is_active:
            logger.warning(f"Login attempt for inactive user: {username}")
            raise AuthenticationFailed('Usuario inactivo')
        
        # Generar tokens
        refresh = RefreshToken.for_user(user)
        
        # Actualizar last_login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        logger.info(f"Successful login for user: {username} (ID: {user.id})")
        
        # TODO: Registrar en tabla de auditoría
        # LoginLog.objects.create(
        #     user=user,
        #     success=True,
        #     ip_address=get_client_ip(request),
        #     user_agent=request.META.get('HTTP_USER_AGENT')
        # )
        
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': user,
        }

    @staticmethod
    def refresh_token(refresh_token: str) -> dict:
        """
        Genera nuevo access token desde refresh token.
        
        Args:
            refresh_token: Refresh token JWT
        
        Returns:
            dict: {'access': str}
        
        Raises:
            ValidationError: Si token inválido
        """
        from rest_framework_simplejwt.tokens import RefreshToken
        from rest_framework_simplejwt.exceptions import TokenError
        
        try:
            refresh = RefreshToken(refresh_token)
            access = str(refresh.access_token)
            
            logger.debug(f"Token refreshed for user_id: {refresh['user_id']}")
            
            return {
                'access': access,
            }
        
        except TokenError as e:
            logger.warning(f"Invalid refresh token: {str(e)}")
            raise ValidationError(f'Token inválido: {str(e)}')

    @staticmethod
    def logout(refresh_token: str) -> None:
        """
        Blacklist refresh token (logout).
        
        Args:
            refresh_token: Refresh token a invalidar
        
        Raises:
            ValidationError: Si token inválido o blacklist no habilitado
        
        NOTA: Access token sigue válido hasta expirar.
        """
        from rest_framework_simplejwt.tokens import RefreshToken
        from rest_framework_simplejwt.exceptions import TokenError
        
        try:
            token = RefreshToken(refresh_token)
            user_id = token['user_id']
            
            # Blacklist
            token.blacklist()
            
            logger.info(f"User {user_id} logged out successfully")
            
            # TODO: Registrar logout en auditoría
            # LoginLog.objects.create(
            #     user_id=user_id,
            #     action='logout',
            #     success=True
            # )
        
        except TokenError as e:
            logger.warning(f"Invalid token during logout: {str(e)}")
            raise ValidationError(f'Token inválido: {str(e)}')
        
        except AttributeError:
            logger.error("Token blacklist not enabled")
            raise ValidationError(
                'Blacklist no configurado. Agrega rest_framework_simplejwt.token_blacklist a INSTALLED_APPS'
            )

    @staticmethod
    def verify_token(token: str) -> dict:
        """
        Verifica validez de access token.
        
        Args:
            token: Access token a verificar
        
        Returns:
            dict: {
                'valid': True,
                'user_id': int,
                'exp': int (unix timestamp)
            }
        
        Raises:
            ValidationError: Si token inválido
        """
        from rest_framework_simplejwt.tokens import AccessToken
        from rest_framework_simplejwt.exceptions import TokenError
        
        try:
            access_token = AccessToken(token)
            
            return {
                'valid': True,
                'user_id': access_token['user_id'],
                'exp': access_token['exp'],
            }
        
        except TokenError as e:
            logger.debug(f"Invalid access token: {str(e)}")
            raise ValidationError(f'Token inválido: {str(e)}')

    @staticmethod
    def get_user_from_token(token: str) -> User:
        """
        Obtiene usuario desde access token.
        
        Args:
            token: Access token
        
        Returns:
            User: Usuario autenticado
        
        Raises:
            ValidationError: Si token inválido
        
        Útil para:
        - WebSockets authentication
        - Background tasks con token
        - Testing
        """
        token_data = AuthService.verify_token(token)
        user_id = token_data['user_id']
        
        try:
            return User.objects.get(id=user_id, is_active=True)
        except User.DoesNotExist:
            raise ValidationError('Usuario no encontrado o inactivo')


class PasswordService:
    """
    Service para gestión de passwords.
    
    Separado de AuthService para Single Responsibility.
    """

    @staticmethod
    def change_password(user: User, old_password: str, new_password: str) -> None:
        """
        Cambia password de usuario.
        
        Args:
            user: Usuario
            old_password: Password actual
            new_password: Password nuevo
        
        Raises:
            ValidationError: Si old_password incorrecto
        """
        if not user.check_password(old_password):
            logger.warning(f"Failed password change attempt for user {user.id}")
            raise ValidationError('Password actual incorrecto')
        
        user.set_password(new_password)
        user.save()
        
        logger.info(f"Password changed successfully for user {user.id}")
        
        # TODO: Enviar email de notificación
        # TODO: Invalidar todos los refresh tokens existentes (security)

    @staticmethod
    def reset_password_request(email: str) -> None:
        """
        Solicita reset de password (envía email).
        
        Args:
            email: Email del usuario
        
        TODO: Implementar
        - Generar token temporal
        - Enviar email con link
        - Token expira en X horas
        """
        # Placeholder para futura implementación
        logger.info(f"Password reset requested for email: {email}")
        raise NotImplementedError("Password reset not implemented yet")

    @staticmethod
    def reset_password_confirm(token: str, new_password: str) -> None:
        """
        Confirma reset de password con token.
        
        Args:
            token: Token de reset (desde email)
            new_password: Nuevo password
        
        TODO: Implementar
        """
        # Placeholder para futura implementación
        logger.info(f"Password reset confirmation with token")
        raise NotImplementedError("Password reset not implemented yet")
