# 📋 Instrucciones para Ejecutar el Software de Cálculo Energético

## 🚀 Inicio Rápido (3 pasos)

### Paso 1: Configurar Backend
```bash
# Abrir terminal o PowerShell
cd "C:\Users\ingen\OneDrive\Escritorio\Software on line horno combustion madera\backend"

# Crear entorno virtual (si no existe)
python -m venv venv

# Activar entorno
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### Paso 2: Iniciar API
```bash
# Ejecutar servidor FastAPI
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# O también puedes usar:
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Paso 3: Acceder a la Aplicación
- **Backend API**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs
- **Frontend**: Abrir `frontend/index.html` en navegador

---

## 🔧 Instrucciones Detalladas

### 1. Configuración del Backend

#### 1.1 Instalar Python
- **Windows**: Descargar desde https://python.org (versión 3.11+)
- **Verificar instalación**:
```bash
python --version
```
Debe mostrar: `Python 3.11.x`

#### 1.2 Instalar Dependencias
```bash
# Navegar al directorio del backend
cd backend

# Crear entorno virtual (si no existe)
python -m venv venv

# Activar entorno
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar todas las dependencias
pip install -r requirements.txt
```

**Si hay errores de instalación, ejecutar:**
```bash
# Actualizar pip
python -m pip install --upgrade pip

# Instalar wheel
pip install wheel
```

### 2. Iniciar el Servidor Backend

#### 2.1 Ejecutar la API
```bash
# Desde el directorio backend con el entorno activado
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Alternativas:**
```bash
# Usando python directamente
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Sin modo reload (para producción)
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### 2.2 Verificar que Funciona
- Visitar http://localhost:8000/docs
- Deberías ver la documentación automática de FastAPI
- Probar el endpoint de salud: http://localhost:8000/api/health

### 3. Acceder al Frontend

#### 3.1 Método 1: Abrir Directamente
1. Navegar a: `frontend/index.html`
2. Hacer doble clic para abrir en el navegador
3. La aplicación cargará automáticamente

#### 3.2 Método 2: Servidor Web Simple (opcional)
```bash
# Instalar servidor simple
pip install python-multipart aiofiles

# Iniciar servidor con soporte de archivos estáticos
cd backend
python -m http.server 8000 --directory ../frontend
```

### 4. Realizar Pruebas

#### 4.1 Probar la API
```bash
# Usando curl
curl -X POST "http://localhost:8000/api/calculate" ^
  -H "Content-Type: application/json" ^
  -d "{\"project_code\":\"TEST-001\",\"document_code\":\"DML-001\",\"analyst\":\"Ingeniero\",\"carbon\":50.29,\"hydrogen\":5.82,\"oxygen\":42.94,\"nitrogen\":0.22,\"sulfur\":0.08,\"ash\":0.66,\"moisture\":35.09,\"flow_rate\":3000,\"reported_PCI\":11367,\"furnace_efficiency\":90,\"excess_air\":30,\"duct_diameter\":30}"
```

#### 4.2 Ejecutar Tests
```bash
# Desde el directorio raíz
python tests/test_combustion.py
```

#### 4.3 Probar con Datos de Ejemplo
1. Abre el frontend en el navegador
2. Los campos ya están prellenados con datos por defecto
3. Haz clic en "Calcular"
4. Revisa los resultados generados

---

## 🧪 Ejemplo de Prueba Rápida

### Datos de Entrada (por defecto):
- **Proyecto**: BIO-2024-001
- **Biomasa**: Bagazo de caña
- **Flujo**: 3000 ton/hora
- **PCI**: 11367 kJ/kg
- **Eficiencia**: 90%
- **Aire exceso**: 30%
- **Diámetro ducto**: 30 pulgadas

### Resultados Esperados:
- **Temperatura gases salida**: ~847°C
- **Velocidad gases**: ~12.3 m/s
- **Eficiencia real**: 90%
- **Energía total**: ~141 MW
- **Energía útil**: ~127 MW

---

## 🔧 Configuración para Desarrollo

### Para Cambiar la API Base URL
En `frontend/js/app.js`, modificar:
```javascript
const appState = {
    currentData: null,
    results: null,
    isLoading: false,
    apiBase: 'http://localhost:8000/api' // Cambiar si es necesario
};
```

### Para Corregir Problemas Comunes

#### Error: Puerto en Uso
```bash
# Verificar qué proceso usa el puerto 8000
netstat -ano | findstr :8000

# Matar el proceso si es necesario
taskkill /PID 1234 /F
```

#### Error: Módulos No Encontrados
```bash
# Instalar dependencias faltantes
pip install <modulo_faltante>
```

#### Error: Import Errors
```bash
# Asegurar estar en el directorio correcto
cd backend
python -c "from app.main import app; print('Importación exitosa')"
```

---

## 🌐 Despliegue en Producción

### Para Render:
1. Conectar el repositorio a GitHub
2. Crear cuenta en [render.com](https://render.com)
3. Conectar repositorio y elegir template "Python FastAPI"
4. Configurar variables de entorno si es necesario
5. Deploy automático en cada push

### Para Docker:
```bash
# Construir imagen
docker build -t biomasa-calculator .

# Ejecutar contenedor
docker run -p 8000:8000 biomasa-calculator
```

---

## 📞 Soporte y Ayuda

### Documentación Técnica:
- **Referencia API**: http://localhost:8000/docs
- **Documento LaTeX**: `docs/calculations.pdf`
- **Código fuente**: Ver archivos en directorio `backend/app/`

### Contacto:
- **Ingeniero Especialista**: Jonathan Arboleda Genes
- **Email**: proyectos2@dmlsas.com
- **Web**: https://www.dmlsas.com/

---

## ✅ Checklist de Verificación

- [ ] Python 3.11+ instalado
- [ ] Entorno virtual creado
- [ ] Dependencias instaladas
- [ ] API corriendo en puerto 8000
- [ ] Frontend accesible
- [ ] Cálculos de prueba funcionando
- [ ] Gráficos generados correctamente
- [ ] Documentación API visible

¡El software está listo para usar! 🎉