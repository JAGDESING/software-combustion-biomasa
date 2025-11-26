# Dockerfile para Biomasa Calculator - DML Ingenieros
# Multi-stage build para optimización

# Etapa 1: Build stage
FROM python:3.11-slim as builder

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y instalar dependencias Python
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Etapa 2: Runtime stage
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar dependencias instaladas desde builder
COPY --from=builder /root/.local /root/.local

# Copiar código de la aplicación
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Crear directorio para archivos temporales
RUN mkdir -p /tmp/uploads

# Exponer puerto
EXPOSE 8000

# Variables de entorno
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Comando de inicio
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Labels para metadata
LABEL maintainer="DML Ingenieros Consultores"
LABEL version="1.0.0"
LABEL description="Sistema de cálculo energético de combustión de biomasa"
LABEL url="https://dmlingenieros.com"