from pydantic import BaseModel
from typing import List, Optional


class CombustionResults(BaseModel):
    """Modelo para resultados de cálculos de combustión"""

    # Propiedades del combustible
    pcs: float  # Poder Calorífico Superior (kJ/kg)
    pci_calculated: float  # PCI calculado (kJ/kg)
    composition_wet_base: dict  # Composición en base húmeda

    # Propiedades del aire
    air_density: float  # Densidad del aire (kg/m³)
    absolute_humidity: float  # Humedad absoluta (kg agua/kg aire seco)
    air_enthalpy: float  # Entalpía del aire húmedo (kJ/kg)

    # Estequiometría
    theoretical_air: float  # Aire teórico requerido (kg/kg combustible)
    real_air: float  # Aire real con exceso (kg/kg combustible)
    excess_air_percentage: float  # Porcentaje de aire en exceso

    # Composición de gases de combustión (kg/kg combustible)
    co2: float
    h2o: float
    so2: float
    o2_excess: float
    n2: float
    total_gas_mass: float

    # Fracciones volumétricas
    co2_fraction_vol: float
    h2o_fraction_vol: float
    so2_fraction_vol: float
    o2_fraction_vol: float
    n2_fraction_vol: float

    # Balance de energía
    total_energy_released: float  # Energía total liberada (MW)
    useful_energy: float  # Energía útil (MW)
    adiabatic_flame_temp: float  # Temperatura adiabática de llama (K)
    outlet_gas_temp: float  # Temperatura gases salida (K)
    chimney_losses: float  # Pérdidas por chimenea (MW)
    real_efficiency: float  # Eficiencia real (%)

    # Dinámica de fluidos
    gas_density: float  # Densidad de gases (kg/m³)
    volumetric_flow: float  # Flujo volumétrico (m³/s)
    duct_area: float  # Área del ducto (m²)
    gas_velocity: float  # Velocidad de gases (m/s)
    reynolds_number: float  # Número de Reynolds
    friction_factor: float  # Factor de fricción
    pressure_drop: float  # Caída de presión (Pa/m)

    # Transferencia de calor
    thermal_resistance: float  # Resistencia térmica total (K·m²/W)
    heat_transfer_coefficient: float  # Coeficiente U (W/(m²·K))
    heat_loss_per_meter: float  # Pérdida de calor por metro (W/m)
    external_wall_temp: float  # Temperatura pared externa (°C)
    refractory_gradient: float  # Gradiente en refractario (°C)
    insulation_efficiency: float  # Eficiencia de aislamiento (%)

    # Emisiones
    co2_emission_factor: float  # Factor de emisión CO₂ (kg/kg)
    co2_concentration_dry: float  # Concentración CO₂ gases secos (%)
    volumetric_heating_value: float  # Poder calorífico volumétrico (kJ/m³)

    # Propiedades para análisis
    flow_rate_kg_s: float  # Flujo en kg/s
    mass_flow_gases: float  # Flujo másico de gases (kg/s)


class SensibilityResults(BaseModel):
    """Modelo para resultados de análisis de sensibilidad"""

    parameter_name: str
    parameter_values: List[float]
    temperatures: List[float]  # Temperaturas para cada valor
    velocities: List[float]  # Velocidades para cada valor
    pressure_drops: List[float]  # Caídas de presión para cada valor
    efficiencies: List[float]  # Eficiencias para cada valor


class ConstantsResponse(BaseModel):
    """Modelo para constantes y valores por defecto"""

    bogotá_conditions: dict
    physical_constants: dict
    typical_values: dict