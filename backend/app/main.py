"""
API principal para cálculos energéticos de combustión de biomasa
FastAPI application
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import os
from pathlib import Path

from .models.biomass import BiomassInput
from .models.results import CombustionResults, SensibilityResults, ConstantsResponse
from .services.combustion import CombustionCalculator
from .services.sensitivity import SensitivityAnalyzer
from .services.atmospheric import AtmosphericCalculator
from .utils.constants import BOGOTA_CONDITIONS, GAS_PROPERTIES

# Crear aplicación FastAPI
app = FastAPI(
    title="API para Cálculos Energéticos de Biomasa",
    description="Sistema de cálculo termodinámico para combustión de biomasa en hornos",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos del frontend
frontend_path = Path("../frontend")
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

# Endpoint principal para servir el frontend
@app.get("/")
async def read_index():
    """Servir la página principal"""
    index_path = Path("../frontend/index.html")
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "API de Cálculos Energéticos de Biomasa - DML Ingenieros"}

@app.post("/api/calculate", response_model=CombustionResults)
async def calculate_combustion(input_data: BiomassInput):
    """
    Calcular todos los parámetros de combustión (38 cálculos)

    Este endpoint realiza el análisis completo del sistema de combustión:
    - Propiedades del combustible
    - Estequiometría y productos
    - Balance de energía
    - Dinámica de fluidos
    - Transferencia de calor
    - Emisiones
    """
    try:
        # Validar datos de entrada
        validation_result = _validate_input(input_data)
        if not validation_result['valid']:
            raise HTTPException(
                status_code=400,
                detail=f"Error en validación: {validation_result['error']}"
            )

        # Crear calculadora y ejecutar cálculos
        calculator = CombustionCalculator(input_data)
        results = calculator.calculate_all()

        return results

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en cálculos: {str(e)}"
        )

@app.post("/api/sensitivity", response_model=SensibilityResults)
async def sensitivity_analysis(
    parameter: str,
    range_percent: float = 50,
    num_points: int = 20,
    input_data: BiomassInput = None
):
    """
    Realizar análisis de sensibilidad para un parámetro específico

    Parámetros disponibles:
    - flow_rate: Flujo de biomasa
    - excess_air: Aire en exceso
    - furnace_efficiency: Eficiencia del horno
    - moisture: Humedad del combustible
    - carbon: % de carbono
    - hydrogen: % de hidrógeno
    """
    try:
        if not input_data:
            # Usar valores por defecto si no se proporcionan
            input_data = BiomassInput()

        # Validar parámetro
        valid_params = [
            'flow_rate', 'excess_air', 'furnace_efficiency',
            'moisture', 'carbon', 'hydrogen', 'oxygen',
            'duct_diameter', 'reported_PCI'
        ]

        if parameter not in valid_params:
            raise HTTPException(
                status_code=400,
                detail=f"Parámetro no válido. Opciones: {', '.join(valid_params)}"
            )

        # Realizar análisis
        analyzer = SensitivityAnalyzer(input_data)
        results = analyzer.analyze_parameter(
            parameter,
            range_percent=range_percent,
            num_points=num_points
        )

        return results

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en análisis de sensibilidad: {str(e)}"
        )

@app.post("/api/multi-sensitivity")
async def multi_parameter_sensitivity(
    parameters: List[str],
    range_percent: float = 30,
    input_data: BiomassInput = None
):
    """
    Análisis de sensibilidad múltiple
    """
    try:
        if not input_data:
            input_data = BiomassInput()

        analyzer = SensitivityAnalyzer(input_data)
        results = analyzer.multi_param_analysis(
            parameters=parameters,
            range_percent=range_percent
        )

        return results

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en análisis múltiple: {str(e)}"
        )

@app.post("/api/optimize")
async def optimize_parameter(
    parameter: str,
    objective: str = "efficiency",
    constraints: Optional[Dict] = None,
    input_data: BiomassInput = None
):
    """
    Optimizar un parámetro para un objetivo específico

    Objetivos disponibles:
    - efficiency: Maximizar eficiencia
    - temperature: Alcanzar temperatura óptima
    - velocity: Optimizar velocidad de gases
    """
    try:
        if not input_data:
            input_data = BiomassInput()

        analyzer = SensitivityAnalyzer(input_data)
        results = analyzer.optimize_parameter(
            parameter_name=parameter,
            objective=objective,
            constraints=constraints or {}
        )

        return results

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en optimización: {str(e)}"
        )

@app.get("/api/constants", response_model=ConstantsResponse)
async def get_constants():
    """
    Obtener constantes físicas y valores por defecto
    """
    return ConstantsResponse(
        bogotá_conditions=BOGOTA_CONDITIONS,
        physical_constants={
            'R_universal': 8.314,  # J/(mol·K)
            'R_air': 287.05,  # J/(kg·K)
            'g': 9.81,  # m/s²
            'air_composition': {
                'O2': 0.232,  # fracción másica
                'N2': 0.768
            }
        },
        typical_values={
            'refractory_conductivity': 0.5,  # W/(m·K)
            'refractory_thickness': 0.15,  # m
            'max_velocity': 20,  # m/s
            'min_efficiency': 70  # %
        }
    )

@app.get("/api/cities")
async def get_cities():
    """
    Obtener lista de ciudades colombianas con condiciones atmosféricas
    """
    cities = AtmosphericCalculator.get_all_cities()
    return {"cities": cities}

@app.get("/api/city/{city_name}")
async def get_city_conditions(city_name: str):
    """
    Obtener condiciones atmosféricas de una ciudad específica
    """
    conditions = AtmosphericCalculator.get_city_conditions(city_name)
    if not conditions:
        raise HTTPException(
            status_code=404,
            detail=f"Ciudad '{city_name}' no encontrada"
        )
    return conditions

@app.post("/api/atmospheric-custom")
async def calculate_atmospheric_conditions(
    altitude: float,
    temperature: float,
    relative_humidity: float
):
    """
    Calcular propiedades atmosféricas para condiciones personalizadas
    """
    try:
        conditions = AtmosphericCalculator.calculate_custom_conditions(
            altitude, temperature, relative_humidity
        )

        # Validar condiciones
        validation = AtmosphericCalculator.validate_conditions(conditions)
        if not validation['is_valid']:
            raise HTTPException(
                status_code=400,
                detail=f"Condiciones inválidas: {', '.join(validation['errors'])}"
            )

        return {
            "conditions": conditions,
            "validation": validation
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en cálculo atmosférico: {str(e)}"
        )

@app.post("/api/export/pdf")
async def export_to_pdf(input_data: BiomassInput):
    """
    Generar reporte PDF con resultados
    """
    try:
        # Realizar cálculos
        calculator = CombustionCalculator(input_data)
        results = calculator.calculate_all()

        # Generar PDF (implementación pendiente)
        pdf_path = _generate_pdf_report(input_data, results)

        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"combustion_report_{input_data.project_code}.pdf"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generando PDF: {str(e)}"
        )

@app.post("/api/export/excel")
async def export_to_excel(input_data: BiomassInput):
    """
    Exportar resultados a Excel
    """
    try:
        # Realizar cálculos
        calculator = CombustionCalculator(input_data)
        results = calculator.calculate_all()

        # Generar Excel (implementación pendiente)
        excel_path = _generate_excel_report(input_data, results)

        return FileResponse(
            excel_path,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=f"combustion_results_{input_data.project_code}.xlsx"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error exportando a Excel: {str(e)}"
        )

@app.get("/api/health")
async def health_check():
    """
    Verificar estado de la API
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "calculate": "/api/calculate",
            "sensitivity": "/api/sensitivity",
            "constants": "/api/constants"
        }
    }

# Funciones auxiliares
def _validate_input(input_data: BiomassInput) -> Dict:
    """
    Validar datos de entrada
    """
    # Verificar que la composición sume 100%
    composition_sum = (input_data.carbon + input_data.hydrogen +
                      input_data.oxygen + input_data.nitrogen +
                      input_data.sulfur + input_data.ash)

    if abs(composition_sum - 100) > 0.5:
        return {
            'valid': False,
            'error': f'La composición en base seca debe sumar 100%. Actual: {composition_sum:.2f}%'
        }

    # Validar rangos lógicos
    if input_data.moisture > 60:
        return {
            'valid': False,
            'error': 'La humedad no puede superar el 60%'
        }

    if input_data.furnace_efficiency > 100 or input_data.furnace_efficiency < 10:
        return {
            'valid': False,
            'error': 'La eficiencia debe estar entre 10% y 100%'
        }

    return {'valid': True}

def _generate_pdf_report(input_data: BiomassInput, results: CombustionResults) -> str:
    """
    Generar reporte PDF (placeholder)
    """
    # TODO: Implementar generación de PDF con reportlab
    # Por ahora retornar placeholder
    return "placeholder.pdf"

def _generate_excel_report(input_data: BiomassInput, results: CombustionResults) -> str:
    """
    Generar reporte Excel (placeholder)
    """
    # TODO: Implementar generación de Excel con openpyxl
    # Por ahora retornar placeholder
    return "placeholder.xlsx"

# Eventos de startup
@app.on_event("startup")
async def startup_event():
    """
    Inicialización de la API
    """
    print("🚀 API de Cálculos Energéticos de Biomasa - DML Ingenieros iniciada")
    print("📊 Documentación disponible en /docs")
    print("🔗 Frontend disponible en /")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Limpieza al apagar la API
    """
    print("🛑 API deteniéndose...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)