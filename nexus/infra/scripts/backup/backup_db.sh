#!/bin/bash
# ==============================================================================
# Backup de PostgreSQL
# ==============================================================================
#
# Uso:
#   ./scripts/backup_db.sh
#   ./scripts/backup_db.sh /ruta/custom/backup
#
# Cron diario (ejemplo):
#   0 2 * * * /path/to/scripts/backup_db.sh >> /var/log/backup.log 2>&1
#
# ==============================================================================

set -e

# Configuración
CONTAINER_NAME="minimum_api_db"
DB_NAME="${DB_NAME:-minimum_api}"
DB_USER="${DB_USER:-postgres}"
BACKUP_DIR="${1:-./backups}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/backup_${DB_NAME}_${TIMESTAMP}.sql"
KEEP_DAYS=7

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🗄️  Iniciando backup de base de datos${NC}"

# Crear directorio si no existe
mkdir -p "$BACKUP_DIR"

# Verificar que el contenedor existe
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${RED}✗ Error: Contenedor ${CONTAINER_NAME} no está corriendo${NC}"
    exit 1
fi

# Crear backup
echo -e "${YELLOW}→ Creando backup: ${BACKUP_FILE}${NC}"
docker exec -t "$CONTAINER_NAME" pg_dump -U "$DB_USER" "$DB_NAME" > "$BACKUP_FILE"

# Comprimir backup
echo -e "${YELLOW}→ Comprimiendo backup...${NC}"
gzip "$BACKUP_FILE"
BACKUP_FILE="${BACKUP_FILE}.gz"

# Verificar que el backup se creó correctamente
if [ -f "$BACKUP_FILE" ]; then
    SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo -e "${GREEN}✓ Backup completado: ${BACKUP_FILE} (${SIZE})${NC}"
else
    echo -e "${RED}✗ Error: El backup falló${NC}"
    exit 1
fi

# Limpiar backups antiguos
echo -e "${YELLOW}→ Limpiando backups antiguos (más de ${KEEP_DAYS} días)...${NC}"
find "$BACKUP_DIR" -name "backup_${DB_NAME}_*.sql.gz" -mtime +$KEEP_DAYS -delete
REMAINING=$(find "$BACKUP_DIR" -name "backup_${DB_NAME}_*.sql.gz" | wc -l)
echo -e "${GREEN}✓ Backups restantes: ${REMAINING}${NC}"

# Resumen
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Backup completado exitosamente${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "Archivo: ${BACKUP_FILE}"
echo -e "Tamaño: ${SIZE}"
echo -e "Fecha: $(date)"
echo ""

# Opcional: Subir a cloud storage (descomentar y configurar)
# echo -e "${YELLOW}→ Subiendo a S3...${NC}"
# aws s3 cp "$BACKUP_FILE" "s3://your-bucket/backups/"