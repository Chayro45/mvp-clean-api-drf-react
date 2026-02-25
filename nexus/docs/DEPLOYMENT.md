# 🚀 Deployment Guide

Guía de despliegue del proyecto (teórica, con fines educativos).

⚠️ **Nota**: Este proyecto no se desplegará en producción, pero esta guía documenta el proceso completo para fines de aprendizaje.

---

## Tabla de Contenidos

- [Consideraciones Pre-Deployment](#consideraciones-pre-deployment)
- [Entornos](#entornos)
- [Deployment con Docker](#deployment-con-docker)
- [Deployment en VPS](#deployment-en-vps)
- [Deployment en Cloud (AWS/GCP/Azure)](#deployment-en-cloud)
- [Configuración de Producción](#configuración-de-producción)
- [CI/CD](#cicd)
- [Monitoreo y Logging](#monitoreo-y-logging)
- [Backups](#backups)
- [Rollback](#rollback)

---

## Consideraciones Pre-Deployment

### Checklist de Seguridad

- [ ] **SECRET_KEY**: Generar nueva y única para producción
- [ ] **DEBUG**: Establecer en `False`
- [ ] **ALLOWED_HOSTS**: Configurar dominio real
- [ ] **CORS_ALLOWED_ORIGINS**: Limitar a dominio del frontend
- [ ] **Passwords**: Cambiar credenciales por defecto (admin, postgres)
- [ ] **HTTPS**: Configurar SSL/TLS
- [ ] **Environment variables**: Nunca commitear secretos
- [ ] **Database**: Usar PostgreSQL (no SQLite)
- [ ] **Static files**: Configurar CDN o servir correctamente
- [ ] **Rate limiting**: Activado y configurado
- [ ] **Firewall**: Permitir solo puertos necesarios

---

### Checklist de Performance

- [ ] **Cache**: Redis configurado
- [ ] **Static files**: Servidos por Nginx/CDN
- [ ] **Media files**: En S3 o storage externo
- [ ] **Database**: Índices optimizados
- [ ] **Queries**: select_related/prefetch_related
- [ ] **Gunicorn**: Workers configurados (CPU * 2 + 1)
- [ ] **Connection pooling**: Configurado
- [ ] **Compression**: Gzip activado

---

## Entornos

### Desarrollo (Local)

```bash
# .env
DEBUG=True
SECRET_KEY=dev-secret-key
DATABASE_URL=postgresql://postgres:postgres@localhost/minimum_api
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Staging (Pre-producción)

```bash
# .env.staging
DEBUG=False
SECRET_KEY=<secret-generado>
DATABASE_URL=postgresql://user:pass@staging-db/minimum_api
ALLOWED_HOSTS=staging.example.com
```

### Producción

```bash
# .env.prod
DEBUG=False
SECRET_KEY=<secret-generado>
DATABASE_URL=postgresql://user:pass@prod-db/minimum_api
ALLOWED_HOSTS=api.example.com
SENTRY_DSN=https://...
```

---

## Deployment con Docker

### 1. Preparar Imágenes de Producción

**Backend Dockerfile.prod:**

```dockerfile
# services/backend/Dockerfile.prod
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Dependencias del sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Recolectar static files
RUN python manage.py collectstatic --noinput

# Usuario no-root
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Gunicorn
CMD ["gunicorn", "config.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--threads", "2", \
     "--timeout", "60", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
```

**Frontend Dockerfile.prod:**

```dockerfile
# services/frontend/Dockerfile.prod
FROM node:20-alpine AS build

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# Nginx para servir
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

### 2. Docker Compose Producción

Ya incluido en `docker-compose.prod.yml` (ver FASE 1).

**Levantar:**

```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

### 3. Nginx Reverse Proxy

**infra/nginx/nginx.conf:**

```nginx
upstream backend {
    server backend:8000;
}

upstream frontend {
    server frontend:80;
}

# HTTP → HTTPS redirect
server {
    listen 80;
    server_name example.com www.example.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS
server {
    listen 443 ssl http2;
    server_name example.com www.example.com;

    # SSL
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Gzip
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    # API
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Admin
    location /admin/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Static files (backend)
    location /static/ {
        alias /var/www/static/;
        expires 30d;
    }

    # Media files
    location /media/ {
        alias /var/www/media/;
        expires 30d;
    }

    # Frontend (SPA)
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        
        # Para SPA routing
        try_files $uri $uri/ /index.html;
    }
}
```

---

### 4. SSL con Let's Encrypt

```bash
# Instalar certbot
sudo apt install certbot python3-certbot-nginx

# Obtener certificado
sudo certbot --nginx -d example.com -d www.example.com

# Auto-renovación (cron)
sudo crontab -e
# Agregar:
0 3 * * * certbot renew --quiet
```

---

## Deployment en VPS

### Servidor Recomendado

- **CPU**: 2 cores mínimo
- **RAM**: 4GB mínimo
- **Disk**: 20GB SSD
- **OS**: Ubuntu 22.04 LTS

**Proveedores**: DigitalOcean, Linode, Vultr, Hetzner

---

### Paso a Paso

#### 1. Preparar Servidor

```bash
# SSH al servidor
ssh root@your-server-ip

# Actualizar sistema
apt update && apt upgrade -y

# Instalar dependencias
apt install -y \
    docker.io \
    docker-compose \
    nginx \
    certbot \
    python3-certbot-nginx

# Crear usuario deploy
adduser deploy
usermod -aG sudo,docker deploy

# Configurar firewall
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

---

#### 2. Clonar Proyecto

```bash
# Como usuario deploy
su - deploy

# Clonar
git clone https://github.com/tu-usuario/minimum-api.git
cd minimum-api

# Configurar .env
cp services/backend/.env.example services/backend/.env
cp services/frontend/.env.example services/frontend/.env

# Editar con valores de producción
nano services/backend/.env
```

---

#### 3. Levantar Servicios

```bash
# Build
docker-compose -f docker-compose.prod.yml build

# Levantar
docker-compose -f docker-compose.prod.yml up -d

# Verificar
docker-compose -f docker-compose.prod.yml ps
```

---

#### 4. Configurar Nginx

```bash
# Copiar config
sudo cp infra/nginx/nginx.conf /etc/nginx/sites-available/minimum-api

# Habilitar
sudo ln -s /etc/nginx/sites-available/minimum-api /etc/nginx/sites-enabled/

# Verificar sintaxis
sudo nginx -t

# Recargar
sudo systemctl reload nginx
```

---

#### 5. SSL

```bash
sudo certbot --nginx -d example.com
```

---

## Deployment en Cloud

### AWS (Amazon Web Services)

#### Opción A: ECS (Elastic Container Service)

```bash
# 1. Push imágenes a ECR
aws ecr create-repository --repository-name minimum-api-backend
aws ecr create-repository --repository-name minimum-api-frontend

docker tag minimum-api-backend:latest <account>.dkr.ecr.us-east-1.amazonaws.com/minimum-api-backend
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/minimum-api-backend

# 2. Crear task definition
# 3. Crear servicio ECS
# 4. Configurar ALB (Application Load Balancer)
```

**Servicios AWS necesarios:**
- ECS (contenedores)
- RDS (PostgreSQL)
- ElastiCache (Redis)
- S3 (static/media files)
- CloudFront (CDN)
- Route53 (DNS)
- ACM (SSL certificates)

---

#### Opción B: EC2

Similar al deployment en VPS, pero con instancia EC2.

---

### GCP (Google Cloud Platform)

#### Cloud Run (Serverless)

```bash
# 1. Build en Cloud Build
gcloud builds submit --tag gcr.io/PROJECT-ID/minimum-api-backend

# 2. Deploy
gcloud run deploy minimum-api-backend \
  --image gcr.io/PROJECT-ID/minimum-api-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

**Servicios GCP necesarios:**
- Cloud Run
- Cloud SQL (PostgreSQL)
- Memorystore (Redis)
- Cloud Storage (files)
- Cloud CDN
- Cloud Load Balancing

---

### Azure

#### Azure Container Instances

```bash
# 1. Push a Azure Container Registry
az acr create --name minimumapi --resource-group myResourceGroup --sku Basic

# 2. Deploy
az container create \
  --resource-group myResourceGroup \
  --name minimum-api-backend \
  --image minimumapi.azurecr.io/backend:latest \
  --dns-name-label minimum-api \
  --ports 8000
```

---

## Configuración de Producción

### settings/prod.py

```python
from .base import *

DEBUG = False

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

# Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Database con connection pooling
DATABASES = {
    'default': {
        **dj_database_url.config(conn_max_age=600),
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}

# Static files en S3
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'

STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/minimum-api/error.log',
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'sentry': {
            'level': 'ERROR',
            'class': 'sentry_sdk.integrations.logging.EventHandler',
        },
    },
    'root': {
        'handlers': ['file', 'sentry'],
        'level': 'INFO',
    },
}

# Sentry
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=env('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,
    send_default_pii=False,
)
```

---

## CI/CD

Ver archivo `.github/workflows/ci.yml` incluido en FASE 3.

**Pipeline básico:**
1. Tests
2. Linting
3. Build Docker images
4. Push a registry
5. Deploy a staging (automático)
6. Deploy a producción (manual approval)

---

## Monitoreo y Logging

### Sentry (Error Tracking)

```bash
pip install sentry-sdk

# settings.py
import sentry_sdk
sentry_sdk.init(dsn="https://...")
```

---

### Prometheus + Grafana (Métricas)

**docker-compose.monitoring.yml:**

```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
  
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

---

### ELK Stack (Logs Centralizados)

- Elasticsearch
- Logstash
- Kibana

---

## Backups

### Automatizar Backups

```bash
# Cron diario
0 2 * * * /path/to/scripts/backup_db.sh

# Subir a S3
aws s3 cp backup.sql.gz s3://backups/$(date +%Y%m%d)/
```

### Probar Restore

```bash
# Al menos mensualmente
make restore FILE=backups/backup_20240101_120000.sql.gz
```

---

## Rollback

### Plan de Rollback

```bash
# 1. Tag antes de deploy
git tag v1.2.3

# 2. Si algo falla, volver al tag anterior
git checkout v1.2.2

# 3. Rebuild y redeploy
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# 4. Verificar
curl https://api.example.com/health/
```

### Blue-Green Deployment

Tener dos entornos (blue y green), deploy en uno, verificar, cambiar DNS/load balancer.

---

## Checklist Final Pre-Launch

- [ ] Todos los tests pasan
- [ ] SSL configurado correctamente
- [ ] Backups automáticos funcionando
- [ ] Monitoring activado (Sentry, Prometheus)
- [ ] Rate limiting testeado
- [ ] Load testing realizado
- [ ] Documentación actualizada
- [ ] DNS configurado
- [ ] Email de errores configurado
- [ ] Plan de rollback documentado

---

## Recursos

- **Django Deployment**: https://docs.djangoproject.com/en/4.2/howto/deployment/
- **Docker Best Practices**: https://docs.docker.com/develop/dev-best-practices/
- **AWS ECS**: https://aws.amazon.com/ecs/
- **Digital Ocean Tutorials**: https://www.digitalocean.com/community/tutorials

---

**Nota**: Este proyecto es educativo y no requiere deployment real, pero esta guía documenta el proceso completo para referencia futura.
