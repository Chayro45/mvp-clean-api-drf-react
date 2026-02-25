FROM python:3.12-slim

# Variables base
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Crear usuario no-root
RUN addgroup --system django && adduser --system --ingroup django django

# Directorio de trabajo
WORKDIR /app

# Dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar proyecto
COPY . .

# Permisos
RUN chown -R django:django /app

# Cambiar a usuario no-root
USER django

# Puerto interno
EXPOSE 8000

# Comando de arranque
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
