"""
Servicio para cálculos de propiedades atmosféricas
"""

from typing import Dict, List
import math
from ..utils.constants import *
from ..utils.equations import *


class AtmosphericCalculator:
    """Calculadora de propiedades atmosféricas por localización"""

    # Base de datos de ciudades colombianas
    CITIES_DATABASE = {
        'Bogotá': {
            'altitude': 2640,
            'avg_temp': 15,
            'avg_humidity': 75,
            'pressure': 746,
            'air_density': 1.00
        },
        'Medellín': {
            'altitude': 1475,
            'avg_temp': 22,
            'avg_humidity': 70,
            'pressure': 845,
            'air_density': 1.05
        },
        'Cali': {
            'altitude': 1018,
            'avg_temp': 24,
            'avg_humidity': 80,
            'pressure': 890,
            'air_density': 1.08
        },
        'Barranquilla': {
            'altitude': 30,
            'avg_temp': 28,
            'avg_humidity': 85,
            'pressure': 1010,
            'air_density': 1.16
        },
        'Bucaramanga': {
            'altitude': 959,
            'avg_temp': 23,
            'avg_humidity': 75,
            'pressure': 895,
            'air_density': 1.09
        },
        'Pereira': {
            'altitude': 1467,
            'avg_temp': 21,
            'avg_humidity': 77,
            'pressure': 846,
            'air_density': 1.06
        },
        'Manizales': {
            'altitude': 2150,
            'avg_temp': 17,
            'avg_humidity': 78,
            'pressure': 780,
            'air_density': 1.02
        },
        'Cúcuta': {
            'altitude': 320,
            'avg_temp': 27,
            'avg_humidity': 70,
            'pressure': 975,
            'air_density': 1.12
        },
        'Ibagué': {
            'altitude': 1285,
            'avg_temp': 21,
            'avg_humidity': 73,
            'pressure': 865,
            'air_density': 1.07
        },
        'Villavicencio': {
            'altitude': 467,
            'avg_temp': 27,
            'avg_humidity': 82,
            'pressure': 955,
            'air_density': 1.10
        }
    }

    @classmethod
    def get_city_conditions(cls, city_name: str) -> Dict:
        """
        Obtener condiciones atmosféricas de una ciudad
        """
        city_name = city_name.title()

        if city_name in cls.CITIES_DATABASE:
            return cls.CITIES_DATABASE[city_name]
        else:
            # Si no está en la base, usar Bogotá por defecto
            return cls.CITIES_DATABASE['Bogotá']

    @classmethod
    def calculate_custom_conditions(cls, altitude: float,
                                  temperature: float,
                                  relative_humidity: float) -> Dict:
        """
        Calcular propiedades atmosféricas para condiciones personalizadas
        """
        # Presión atmosférica
        pressure = pressure_altitude(altitude)  # kPa

        # Densidad del aire
        temp_k = temperature + 273.15
        pressure_pa = pressure * 1000
        air_density = pressure_pa / (R_AIR * temp_k)

        # Humedad absoluta
        abs_humidity = absolute_humidity(
            relative_humidity,
            temperature,
            pressure
        )

        # Entalpía del aire húmedo
        air_enthalpy = moist_air_enthalpy(temperature, abs_humidity)

        # Presión de vapor saturado
        vapor_pressure = saturated_vapor_pressure(temperature)  # mmHg

        return {
            'altitude': altitude,
            'temperature': temperature,
            'relative_humidity': relative_humidity,
            'pressure': pressure,
            'air_density': air_density,
            'absolute_humidity': abs_humidity,
            'air_enthalpy': air_enthalpy,
            'vapor_pressure': vapor_pressure,
            'oxygen_fraction': cls._calculate_oxygen_fraction(altitude)
        }

    @classmethod
    def _calculate_oxygen_fraction(cls, altitude: float) -> float:
        """
        Calcular fracción de oxígeno disponible basada en altitud
        """
        # Simplificación: disminución lineal con altitud
        oxygen_sea_level = 0.21
        oxygen_reduction = altitude * 0.000005  # 0.0005 por cada metro

        oxygen_fraction = max(oxygen_sea_level - oxygen_reduction, 0.15)
        return oxygen_fraction

    @classmethod
    def get_all_cities(cls) -> List[Dict]:
        """
        Obtener lista de todas las ciudades disponibles
        """
        cities_list = []
        for city, data in cls.CITIES_DATABASE.items():
            city_info = data.copy()
            city_info['name'] = city
            cities_list.append(city_info)

        # Ordenar por altitud
        cities_list.sort(key=lambda x: x['altitude'])
        return cities_list

    @classmethod
    def compare_conditions(cls, condition1: Dict, condition2: Dict) -> Dict:
        """
        Comparar dos condiciones atmosféricas
        """
        comparison = {}

        for key in ['pressure', 'air_density', 'temperature', 'relative_humidity']:
            if key in condition1 and key in condition2:
                val1 = condition1[key]
                val2 = condition2[key]
                if val1 != 0:
                    diff_percent = ((val2 - val1) / val1) * 100
                else:
                    diff_percent = 0

                comparison[key] = {
                    'condition1': val1,
                    'condition2': val2,
                    'difference': val2 - val1,
                    'percent_change': diff_percent
                }

        # Impacto en combustión
        impact = cls._estimate_combustion_impact(comparison)
        comparison['combustion_impact'] = impact

        return comparison

    @classmethod
    def _estimate_combustion_impact(cls, comparison: Dict) -> Dict:
        """
        Estimar impacto de las diferencias atmosféricas en la combustión
        """
        impacts = []

        # Impacto por densidad del aire
        if 'air_density' in comparison:
            air_density_change = comparison['air_density']['percent_change']
            if abs(air_density_change) > 5:
                impacts.append({
                    'factor': 'Densidad del aire',
                    'impact': f"Cambio del {air_density_change:.1f}% en oxígeno disponible",
                    'recommendation': 'Ajustar relación aire-combustible' if air_density_change > 0 else 'Reducir aire en exceso'
                })

        # Impacto por temperatura
        if 'temperature' in comparison:
            temp_change = comparison['temperature']['difference']
            if abs(temp_change) > 5:
                impacts.append({
                    'factor': 'Temperatura ambiente',
                    'impact': f"Cambio de {temp_change:.1f}°C afecta temperatura de llama",
                    'recommendation': 'Monitorear temperatura de gases'
                })

        # Impacto por humedad
        if 'relative_humidity' in comparison:
            humidity_change = comparison['relative_humidity']['difference']
            if abs(humidity_change) > 10:
                impacts.append({
                    'factor': 'Humedad relativa',
                    'impact': f"Cambio del {humidity_change:.1f}% en humedad del aire de combustión",
                    'recommendation': 'Ajustar cálculo de agua en combustión'
                })

        return {
            'impacts': impacts,
            'overall_risk': 'High' if len(impacts) > 2 else 'Medium' if len(impacts) > 0 else 'Low',
            'needs_adjustment': len(impacts) > 0
        }

    @classmethod
    def generate_atmospheric_report(cls, conditions: Dict) -> str:
        """
        Generar reporte de condiciones atmosféricas
        """
        report = f"""
REPORTE DE CONDICIONES ATMOSFÉRICAS
=================================

Ubicación: {conditions.get('name', 'Personalizado')}
Altitud: {conditions['altitude']:.0f} msnm
Temperatura: {conditions['temperature']:.1f}°C
Humedad Relativa: {conditions['relative_humidity']:.1f}%

PROPIEDADES CALCULADAS:
------------------------
Presión Atmosférica: {conditions['pressure']:.1f} kPa ({conditions['pressure']*7.50062:.1f} mmHg)
Densidad del Aire: {conditions['air_density']:.3f} kg/m³
Humedad Absoluta: {conditions['absolute_humidity']:.4f} kg agua/kg aire seco
Entalpía del Aire: {conditions['air_enthalpy']:.1f} kJ/kg aire seco
Fracción de Oxígeno: {conditions['oxygen_fraction']*100:.2f}% en volumen

COMPARACIÓN CON NIVEL DEL MAR:
------------------------------
Densidad: {(conditions['air_density']/1.225)*100:.1f}% del valor a nivel del mar
Oxígeno disponible: {(conditions['oxygen_fraction']/0.21)*100:.1f}% del valor a nivel del mar

RECOMENDACIONES PARA COMBUSTIÓN:
---------------------------------
"""

        # Añadir recomendaciones específicas
        if conditions['altitude'] > 2000:
            report += "- Alta altitud: Aumentar 15-25% de aire volumétrico\n"
        if conditions['relative_humidity'] > 80:
            report += "- Alta humedad: Considerar precalentamiento del aire\n"
        if conditions['temperature'] < 10:
            report += "- Baja temperatura: Mayor tiempo de precalentamiento requerido\n"

        return report

    @classmethod
    def altitude_correction_factor(cls, altitude: float) -> float:
        """
        Calcular factor de corrección por altitud para flujo volumétrico
        """
        # Corrección basada en densidad del aire
        pressure_ratio = pressure_altitude(altitude) / 101.325  # kPa
        # Asumiendo temperatura constante
        correction_factor = 101.325 / pressure_ratio
        return correction_factor

    @classmethod
    def validate_conditions(cls, conditions: Dict) -> Dict:
        """
        Validar si las condiciones atmosféricas están dentro de rangos razonables
        """
        validation = {
            'is_valid': True,
            'warnings': [],
            'errors': []
        }

        # Validar rangos
        if conditions['altitude'] < 0 or conditions['altitude'] > 5000:
            validation['errors'].append('Altitud fuera de rango (0-5000 m)')
            validation['is_valid'] = False

        if conditions['temperature'] < -20 or conditions['temperature'] > 50:
            validation['errors'].append('Temperatura fuera de rango (-20 a 50°C)')
            validation['is_valid'] = False

        if conditions['relative_humidity'] < 0 or conditions['relative_humidity'] > 100:
            validation['errors'].append('Humedad relativa debe estar entre 0 y 100%')
            validation['is_valid'] = False

        # Advertencias
        if conditions['altitude'] > 3000:
            validation['warnings'].append('Altitud elevada puede requerir ajustes significativos')

        if conditions['relative_humidity'] > 90:
            validation['warnings'].append('Alta humedad puede afectar eficiencia de combustión')

        if conditions['pressure'] < 70:
            validation['warnings'].append('Baja presión atmosférica detectada')

        return validation