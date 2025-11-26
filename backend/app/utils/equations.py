"""
Biblioteca de ecuaciones para cálculos termodinámicos de combustión
"""

import math
from .constants import *


def pressure_altitude(altitude_meters: float) -> float:
    """
    Calcular presión atmosférica basada en altitud
    Ecuación barométrica estándar
    """
    P0 = 101.325  # kPa (nivel del mar)
    L = 0.0065  # K/m (tasa de lapse)
    T0 = 288.15  # K (temperatura estándar)
    g = 9.81  # m/s²
    M = 0.02896  # kg/mol (masa molar aire)
    R = 8.314  # J/(mol·K)

    if altitude_meters < 11000:  # Troposfera
        exponent = -(g * M) / (R * L)
        temp_ratio = 1 - (L * altitude_meters) / T0
        P = P0 * math.pow(temp_ratio, exponent)
        return P
    else:
        # Simplificación para altitudes mayores
        return P0 * math.exp(-altitude_meters / 8500)


def saturated_vapor_pressure(temp_celsius: float) -> float:
    """
    Calcular presión de vapor saturado usando ecuación de Antoine
    Retorna presión en mmHg
    """
    A = ANTOINE_WATER['A']
    B = ANTOINE_WATER['B']
    C = ANTOINE_WATER['C']

    log10_P = A - B / (C + temp_celsius)
    P_mmHg = math.pow(10, log10_P)
    return P_mmHg


def absolute_humidity(relative_humidity: float, dry_bulb_temp: float,
                     atmospheric_pressure: float) -> float:
    """
    Calcular humedad absoluta del aire
    Retorna kg agua / kg aire seco
    """
    # Presión de vapor saturado
    P_sat = saturated_vapor_pressure(dry_bulb_temp)  # mmHg

    # Presión parcial de vapor
    P_v = (relative_humidity / 100) * P_sat  # mmHg

    # Convertir a misma unidad que presión atmosférica
    P_v_kPa = P_v * CONVERSION_FACTORS['mmhg_to_kpa']

    # Humedad absoluta
    w = 0.622 * P_v_kPa / (atmospheric_pressure - P_v_kPa)
    return w


def moist_air_enthalpy(temp_celsius: float, absolute_humidity: float) -> float:
    """
    Calcular entalpía del aire húmedo
    Retorna kJ/kg aire seco
    """
    h_air = 1.006 * temp_celsius
    h_water = absolute_humidity * (2501 + 1.86 * temp_celsius)
    return h_air + h_water


def dulong_heating_value(carbon: float, hydrogen: float, oxygen: float,
                        sulfur: float, ash: float, moisture: float = 0) -> dict:
    """
    Calcular PCS y PCI usando correlación de Dulong
    Entrada en % base seca
    Retorna PCS y PCI en kJ/kg
    """
    # Ajustar a 100% base seca
    total = carbon + hydrogen + oxygen + sulfur + ash
    if total != 100:
        carbon = carbon * 100 / total
        hydrogen = hydrogen * 100 / total
        oxygen = oxygen * 100 / total
        sulfur = sulfur * 100 / total
        ash = ash * 100 / total

    # Poder Calorífico Superior (kJ/kg)
    PCS = 338.2 * carbon + 1442.8 * (hydrogen - oxygen/8) + 94.2 * sulfur

    # Poder Calorífico Inferior
    # Agua de combustión (9H + humedad)
    water_combustion = 9 * hydrogen + moisture
    PCI = PCS - HV_WATER * water_combustion / 100

    return {
        'PCS': PCS,
        'PCI': PCI,
        'water_from_combustion': water_combustion
    }


def theoretical_air_fuel_ratio(carbon: float, hydrogen: float,
                              oxygen: float, sulfur: float) -> float:
    """
    Calcular relación teórica aire/combustible
    Retorna kg aire / kg combustible
    """
    # Oxígeno estequiométrico requerido (kg O₂/kg combustible)
    O2_required = (2.667 * carbon + 8 * hydrogen -
                   1.333 * oxygen + 2 * sulfur) / 100

    # Aire teórico (considerando 23.2% O₂ en masa)
    air_theoretical = O2_required / 0.232

    return air_theoretical


def combustion_products(carbon: float, hydrogen: float, sulfur: float,
                       moisture: float, ash: float,
                       excess_air_percent: float) -> dict:
    """
    Calcular productos de combustión en kg/kg combustible
    """
    # Base seca a base húmeda
    moisture_factor = (100 - moisture) / 100

    # Productos estequiométricos
    CO2 = 3.67 * carbon * moisture_factor / 100  # 44/12 = 3.67
    H2O_from_combustion = 9 * hydrogen * moisture_factor / 100
    H2O_from_fuel = moisture / 100
    H2O_total = H2O_from_combustion + H2O_from_fuel
    SO2 = 2 * sulfur * moisture_factor / 100  # 64/32 = 2

    # Aire y nitrógeno
    air_theoretical = theoretical_air_fuel_ratio(
        carbon * moisture_factor,
        hydrogen * moisture_factor,
        oxygen * moisture_factor,
        sulfur * moisture_factor
    )

    air_real = air_theoretical * (1 + excess_air_percent / 100)

    O2_excess = 0.232 * air_theoretical * (excess_air_percent / 100)
    N2_from_air = 0.768 * air_real

    # Cenizas
    ash_mass = ash * moisture_factor / 100

    return {
        'CO2': CO2,
        'H2O': H2O_total,
        'SO2': SO2,
        'O2': O2_excess,
        'N2': N2_from_air,
        'ash': ash_mass,
        'air_real': air_real,
        'total_gases': CO2 + H2O_total + SO2 + O2_excess + N2_from_air
    }


def gas_density(temperature_k: float, pressure_pa: float,
                composition: dict) -> float:
    """
    Calcular densidad de mezcla de gases usando ley de gases ideales
    Retorna kg/m³
    """
    # Calcular masa molar promedio
    total_moles = 0
    total_mass = 0

    for gas, mass_kg in composition.items():
        if gas in GAS_PROPERTIES:
            moles = mass_kg / (GAS_PROPERTIES[gas]['molar_mass'] / 1000)
            total_moles += moles
            total_mass += mass_kg

    # Masa molar promedio
    avg_molar_mass = total_mass / total_moles if total_moles > 0 else 0

    # Densidad usando ley de gases ideales
    density = (pressure_pa * avg_molar_mass) / (R_UNIVERSAL * temperature_k)
    return density


def reynolds_number(velocity: float, diameter: float, density: float,
                   viscosity: float = 1.8e-5) -> float:
    """
    Calcular número de Reynolds
    Viscosidad dinámica del aire ~1.8e-5 Pa·s a 20°C
    """
    Re = (density * velocity * diameter) / viscosity
    return Re


def colebrook_friction_factor(Re: float, diameter: float,
                            roughness: float = 0.00015) -> float:
    """
    Calcular factor de fricción usando ecuación de Colebrook-White
    Método iterativo
    """
    if Re < 2300:
        # Flujo laminar
        return 64 / Re
    else:
        # Flujo turbulento - iteración
        f = 0.02  # Valor inicial
        for _ in range(10):  # Máximo 10 iteraciones
            numerator = roughness / diameter
            denominator = 3.7 * Re * math.sqrt(f)
            f_new = 1 / math.pow(-2 * math.log10(numerator + denominator), 2)

            if abs(f_new - f) < 1e-6:
                break
            f = f_new

        return f


def pressure_drop_per_length(friction_factor: float, density: float,
                           velocity: float, diameter: float) -> float:
    """
    Calcular caída de presión por unidad de longitud
    Ecuación de Darcy-Weisbach
    Retorna Pa/m
    """
    delta_P = friction_factor * (1 / diameter) * (density * velocity**2 / 2)
    return delta_P


def adiabatic_flame_temperature(fuel_properties: dict,
                              air_fuel_ratio: float) -> float:
    """
    Calcular temperatura adiabática de llama
    Simplificación - requiere iteración
    """
    # Temperatura inicial
    T_ad = 2000  # K (estimación inicial)
    T_ambient = 298  # K

    # Iteración simple (método de Newton-Raphson)
    for _ in range(20):
        # Calor liberado por combustión (simplificado)
        Q_comb = fuel_properties['PCI'] * 1000  # J/kg

        # Cp promedio de productos (valor típico)
        Cp_products = 1.2  # kJ/(kg·K)

        # Balance de energía
        T_ad_new = T_ambient + Q_comb / (air_fuel_ratio * Cp_products)

        if abs(T_ad_new - T_ad) < 1:
            break
        T_ad = T_ad_new

    return T_ad