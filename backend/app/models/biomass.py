from pydantic import BaseModel, Field
from typing import Optional


class BiomassInput(BaseModel):
    """Modelo para datos de entrada de biomasa"""

    # Datos del proyecto
    project_code: str = Field(..., description="Código del proyecto")
    document_code: str = Field(..., description="Código del documento")
    analyst: str = Field(..., description="Nombre del analista")

    # Datos ambientales
    city: str = Field(default="Bogotá", description="Ciudad")
    altitude: float = Field(default=2640, description="Altura sobre el nivel del mar (m)")
    relative_humidity: float = Field(default=75, description="Humedad relativa (%)")
    dry_bulb_temp: float = Field(default=15, description="Temperatura de bulbo seco (°C)")

    # Datos para análisis
    biomass_type: str = Field(default="Bagazo de caña", description="Tipo de biomasa")
    reported_pci: float = Field(default=11367, description="Poder calorífico inferior reportado (kJ/kg)")
    furnace_efficiency: float = Field(default=90, description="Eficiencia del horno (%)")
    excess_air: float = Field(default=30, description="Aire en exceso (%)")
    duct_diameter: float = Field(default=30, description="Diámetro interno ducto (pulgadas)")

    # Composición elemental en base seca (%)
    carbon: float = Field(default=50.29, ge=0, le=100, description="Carbono en base seca (%)")
    hydrogen: float = Field(default=5.82, ge=0, le=100, description="Hidrógeno en base seca (%)")
    oxygen: float = Field(default=42.94, ge=0, le=100, description="Oxígeno en base seca (%)")
    nitrogen: float = Field(default=0.22, ge=0, le=100, description="Nitrógeno en base seca (%)")
    sulfur: float = Field(default=0.08, ge=0, le=100, description="Azufre en base seca (%)")
    ash: float = Field(default=0.66, ge=0, le=100, description="Cenizas en base seca (%)")
    moisture: float = Field(default=35.09, ge=0, le=100, description="Humedad total (%)")

    # Flujo de biomasa
    flow_rate: float = Field(default=3000, description="Flujo de biomasa (ton/hora)")

    class Config:
        schema_extra = {
            "example": {
                "project_code": "BIO-2024-001",
                "document_code": "DML-TECH-001",
                "analyst": "Ing. Juan Pérez",
                "city": "Bogotá",
                "altitude": 2640,
                "relative_humidity": 75,
                "dry_bulb_temp": 15,
                "biomass_type": "Bagazo de caña",
                "reported_PCI": 11367,
                "furnace_efficiency": 90,
                "excess_air": 30,
                "duct_diameter": 30,
                "carbon": 50.29,
                "hydrogen": 5.82,
                "oxygen": 42.94,
                "nitrogen": 0.22,
                "sulfur": 0.08,
                "ash": 0.66,
                "moisture": 35.09,
                "flow_rate": 3000
            }
        }