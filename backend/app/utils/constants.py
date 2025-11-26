"""
Constantes físicas y factores de conversión para cálculos de combustión
"""

# Constantes universales
R_UNIVERSAL = 8.314  # J/(mol·K) - Constante universal de los gases
R_AIR = 287.05  # J/(kg·K) - Constante específica del aire seco
G = 9.81  # m/s² - Aceleración gravitacional

# Pesos atómicos (g/mol)
ATOMIC_WEIGHTS = {
    'C': 12.011,
    'H': 1.008,
    'O': 15.999,
    'N': 14.007,
    'S': 32.06
}

# Calores de combustión estándar (kJ/kg)
HEAT_OF_COMBUSTION = {
    'C': 32790,  # Carbono a CO₂
    'H': 141800,  # Hidrógeno a H₂O
    'S': 9050    # Azufre a SO₂
}

# Calor latente de vaporización del agua
HV_WATER = 2442  # kJ/kg a 25°C

# Factores de conversión
CONVERSION_FACTORS = {
    'kg_to_ton': 0.001,
    'ton_to_kg': 1000,
    'hour_to_sec': 3600,
    'sec_to_hour': 1/3600,
    'kj_to_mj': 0.001,
    'mj_to_kj': 1000,
    'inch_to_m': 0.0254,
    'm_to_inch': 39.3701,
    'pa_to_kpa': 0.001,
    'kpa_to_pa': 1000,
    'mmhg_to_kpa': 0.133322,
    'kpa_to_mmhg': 7.50062
}

# Condiciones estándar de Bogotá
BOGOTA_CONDITIONS = {
    'altitude': 2640,  # msnm
    'pressure': 746,   # mmHg
    'temperature': 15,  # °C
    'humidity': 75,    # %
    'air_density': 1.00,  # kg/m³
    'oxygen_concentration': 0.195  # fracción másica
}

# Coeficientes ecuación de Antoine para agua (presión en mmHg, T en °C)
ANTOINE_WATER = {
    'A': 8.07131,
    'B': 1730.63,
    'C': 233.426
}

# Propiedades típicas de gases a 298 K
GAS_PROPERTIES = {
    'CO2': {
        'molar_mass': 44.01,  # g/mol
        'Cp': 0.844,  # kJ/(kg·K)
        'density': 1.977  # kg/m³
    },
    'H2O': {
        'molar_mass': 18.015,
        'Cp': 1.86,  # vapor
        'density': 0.804  # vapor
    },
    'O2': {
        'molar_mass': 31.999,
        'Cp': 0.918,
        'density': 1.429
    },
    'N2': {
        'molar_mass': 28.014,
        'Cp': 1.04,
        'density': 1.251
    },
    'SO2': {
        'molar_mass': 64.066,
        'Cp': 0.64,
        'density': 2.927
    },
    'AIR': {
        'molar_mass': 28.97,
        'Cp': 1.005,
        'density': 1.225  # a nivel del mar
    }
}

# Composición del aire seco (fracción másica)
AIR_COMPOSITION = {
    'O2': 0.232,
    'N2': 0.768
}

# Propiedades de materiales refractarios típicos
REFRACTORY_PROPERTIES = {
    'thermal_conductivity': 0.5,  # W/(m·K)
    'thickness': 0.15,  # m
    'emissivity': 0.8,
    'roughness': 0.00015  # m (rugosidad absoluta)
}

# Límites de diseño
DESIGN_LIMITS = {
    'max_velocity': 20,  # m/s - velocidad máxima en ductos
    'max_pressure_drop': 500,  # Pa/m - caída de presión máxima
    'min_efficiency': 70,  # % - eficiencia mínima aceptable
    'max_temp_external': 60  # °C - temperatura externa máxima
}