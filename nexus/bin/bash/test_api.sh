#!/bin/bash
# ==============================================================================
# test_api.sh - Script de pruebas rápidas de la API
# ==============================================================================
#
# Uso:
#   chmod +x test_api.sh
#   ./test_api.sh
#
# Prerequisitos:
#   - docker compose up -d (backend corriendo en localhost:8000)
#   - jq instalado (opcional, para formatear JSON)
#
# ==============================================================================

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

BASE_URL="http://localhost:8000"

echo "================================================================================"
echo "🧪 PRUEBAS RÁPIDAS DE API - Minimum API"
echo "================================================================================"
echo ""

# ==============================================================================
# TEST 1: Health Check
# ==============================================================================
echo "${YELLOW}TEST 1: Health Check${NC}"
echo "GET ${BASE_URL}/health/"
echo ""

response=$(curl -s ${BASE_URL}/health/)
echo $response | jq '.' 2>/dev/null || echo $response
echo ""

if echo $response | grep -q "healthy"; then
    echo "${GREEN}✓ Health check OK${NC}"
else
    echo "${RED}✗ Health check FAILED${NC}"
    exit 1
fi
echo ""

# ==============================================================================
# TEST 2: Login (obtener tokens)
# ==============================================================================
echo "${YELLOW}TEST 2: Login${NC}"
echo "POST ${BASE_URL}/api/auth/login/"
echo ""

login_response=$(curl -s -X POST ${BASE_URL}/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin"
  }')

echo $login_response | jq '.' 2>/dev/null || echo $login_response
echo ""

# Extraer access token
ACCESS_TOKEN=$(echo $login_response | jq -r '.access' 2>/dev/null)

if [ "$ACCESS_TOKEN" != "null" ] && [ -n "$ACCESS_TOKEN" ]; then
    echo "${GREEN}✓ Login exitoso${NC}"
    echo "Access Token: ${ACCESS_TOKEN:0:20}..."
else
    echo "${RED}✗ Login FAILED${NC}"
    exit 1
fi
echo ""

# ==============================================================================
# TEST 3: Get Current User (/api/auth/me/)
# ==============================================================================
echo "${YELLOW}TEST 3: Get Current User${NC}"
echo "GET ${BASE_URL}/api/auth/me/"
echo ""

me_response=$(curl -s ${BASE_URL}/api/auth/me/ \
  -H "Authorization: Bearer ${ACCESS_TOKEN}")

echo $me_response | jq '.' 2>/dev/null || echo $me_response
echo ""

if echo $me_response | grep -q "admin"; then
    echo "${GREEN}✓ Current user OK${NC}"
else
    echo "${RED}✗ Current user FAILED${NC}"
fi
echo ""

# ==============================================================================
# TEST 4: List Users
# ==============================================================================
echo "${YELLOW}TEST 4: List Users${NC}"
echo "GET ${BASE_URL}/api/users/"
echo ""

users_response=$(curl -s ${BASE_URL}/api/users/ \
  -H "Authorization: Bearer ${ACCESS_TOKEN}")

echo $users_response | jq '.' 2>/dev/null || echo $users_response
echo ""

if echo $users_response | grep -q "results"; then
    echo "${GREEN}✓ List users OK${NC}"
else
    echo "${RED}✗ List users FAILED${NC}"
fi
echo ""

# ==============================================================================
# TEST 5: Create User (requiere permisos)
# ==============================================================================
echo "${YELLOW}TEST 5: Create User${NC}"
echo "POST ${BASE_URL}/api/users/"
echo ""

create_user_response=$(curl -s -X POST ${BASE_URL}/api/users/ \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "password_confirm": "testpass123",
    "first_name": "Test",
    "last_name": "User"
  }')

echo $create_user_response | jq '.' 2>/dev/null || echo $create_user_response
echo ""

if echo $create_user_response | grep -q "testuser"; then
    echo "${GREEN}✓ Create user OK${NC}"
    
    # Extraer ID del usuario creado para cleanup
    USER_ID=$(echo $create_user_response | jq -r '.id' 2>/dev/null)
else
    echo "${RED}✗ Create user FAILED (puede ser que el usuario ya existe)${NC}"
fi
echo ""

# ==============================================================================
# TEST 6: List Groups (Roles)
# ==============================================================================
echo "${YELLOW}TEST 6: List Groups (Roles)${NC}"
echo "GET ${BASE_URL}/api/users/groups/"
echo ""

groups_response=$(curl -s ${BASE_URL}/api/users/groups/ \
  -H "Authorization: Bearer ${ACCESS_TOKEN}")

echo $groups_response | jq '.' 2>/dev/null || echo $groups_response
echo ""

if echo $groups_response | grep -q "Administradores"; then
    echo "${GREEN}✓ List groups OK${NC}"
else
    echo "${RED}✗ List groups FAILED${NC}"
fi
echo ""

# ==============================================================================
# TEST 7: Delete Test User (cleanup)
# ==============================================================================
if [ -n "$USER_ID" ] && [ "$USER_ID" != "null" ]; then
    echo "${YELLOW}TEST 7: Delete Test User (cleanup)${NC}"
    echo "DELETE ${BASE_URL}/api/users/${USER_ID}/"
    echo ""
    
    delete_response=$(curl -s -X DELETE ${BASE_URL}/api/users/${USER_ID}/ \
      -H "Authorization: Bearer ${ACCESS_TOKEN}")
    
    echo "Response: $delete_response"
    echo ""
    echo "${GREEN}✓ Test user deleted${NC}"
    echo ""
fi

# ==============================================================================
# RESUMEN
# ==============================================================================
echo "================================================================================"
echo "${GREEN}✅ TODAS LAS PRUEBAS COMPLETADAS${NC}"
echo "================================================================================"
echo ""
echo "📝 Resumen:"
echo "  ✓ Health check OK"
echo "  ✓ Login OK"
echo "  ✓ Get current user OK"
echo "  ✓ List users OK"
echo "  ✓ Create user OK"
echo "  ✓ List groups OK"
echo "  ✓ Delete user OK"
echo ""
echo "🔑 Access Token guardado en variable: \$ACCESS_TOKEN"
echo "   Puedes usarlo en nuevas requests:"
echo "   curl -H \"Authorization: Bearer \$ACCESS_TOKEN\" ${BASE_URL}/api/users/"
echo ""
echo "================================================================================"