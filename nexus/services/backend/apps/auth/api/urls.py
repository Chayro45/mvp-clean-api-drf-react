"""
apps/auth/api/urls.py

URLs para endpoints de autenticación.

Rutas:
- POST /api/auth/login/     → Login
- POST /api/auth/refresh/   → Refresh token
- POST /api/auth/logout/    → Logout
- POST /api/auth/verify/    → Verify token
- GET  /api/auth/me/        → Current user
"""
from django.urls import path
from apps.auth.api.views import (
    LoginView,
    TokenRefreshView,
    LogoutView,
    VerifyTokenView,
    CurrentUserView,
)

app_name = 'auth'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('verify/', VerifyTokenView.as_view(), name='verify'),
    path('me/', CurrentUserView.as_view(), name='me'),
]
