"""
Servicio para análisis de sensibilidad dinámico
"""

from typing import List, Dict
import numpy as np
from .combustion import CombustionCalculator
from ..models.biomass import BiomassInput


class SensitivityAnalyzer:
    """Analizador de sensibilidad para parámetros del sistema"""

    def __init__(self, base_input: BiomassInput):
        self.base_input = base_input
        self.calculator = CombustionCalculator(base_input)

    def analyze_parameter(self, parameter_name: str,
                         range_percent: float = 50,
                         num_points: int = 20) -> Dict:
        """
        Analizar sensibilidad de un parámetro
        """
        # Obtener valor base
        base_value = getattr(self.base_input, parameter_name)

        # Generar rango de valores
        min_val = base_value * (1 - range_percent / 100)
        max_val = base_value * (1 + range_percent / 100)
        values = np.linspace(min_val, max_val, num_points).tolist()

        # Ejecutar análisis
        results = self.calculator.sensitivity_analysis(parameter_name, values)

        # Calcular métricas de sensibilidad
        sensitivity_metrics = self._calculate_sensitivity_metrics(
            values, results.temperatures, results.velocities,
            results.pressure_drops, results.efficiencies
        )

        return {
            'parameter': parameter_name,
            'base_value': base_value,
            'unit': self._get_parameter_unit(parameter_name),
            'values': values,
            'results': results,
            'metrics': sensitivity_metrics
        }

    def multi_param_analysis(self, parameters: List[str],
                           range_percent: float = 30) -> Dict:
        """
        Análisis de sensibilidad múltiple
        """
        analysis_results = {}

        for param in parameters:
            analysis_results[param] = self.analyze_parameter(
                param, range_percent, 15
            )

        # Identificar parámetros más sensibles
        sensitivity_ranking = self._rank_sensitivity(analysis_results)

        return {
            'individual_analysis': analysis_results,
            'sensitivity_ranking': sensitivity_ranking,
            'recommendations': self._generate_recommendations(analysis_results)
        }

    def _calculate_sensitivity_metrics(self, values: List[float],
                                     temperatures: List[float],
                                     velocities: List[float],
                                     pressure_drops: List[float],
                                     efficiencies: List[float]) -> Dict:
        """
        Calcular métricas de sensibilidad
        """
        # Calcular derivadas numéricas
        def calculate_derivative(y_values):
            x = np.array(values)
            y = np.array(y_values)
            dy_dx = np.gradient(y, x)
            return dy_dx.tolist()

        # Sensibilidad relativa
        def relative_sensitivity(base_y, dy_dx):
            return (dy_dx * values[0] / base_y * 100).tolist() if base_y != 0 else [0]

        # Calcular métricas para cada variable
        temp_derivative = calculate_derivative(temperatures)
        vel_derivative = calculate_derivative(velocities)
        pressure_derivative = calculate_derivative(pressure_drops)
        eff_derivative = calculate_derivative(efficiencies)

        # Sensibilidades relativas
        temp_rel_sens = relative_sensitivity(temperatures[0], temp_derivative)
        vel_rel_sens = relative_sensitivity(velocities[0], vel_derivative)
        eff_rel_sens = relative_sensitivity(efficiencies[0], eff_derivative)

        # Máxima sensibilidad absoluta
        max_temp_sens = max(abs(d) for d in temp_rel_sens)
        max_vel_sens = max(abs(d) for d in vel_rel_sens)
        max_eff_sens = max(abs(d) for d in eff_rel_sens)

        return {
            'derivatives': {
                'temperature': temp_derivative,
                'velocity': vel_derivative,
                'pressure_drop': pressure_derivative,
                'efficiency': eff_derivative
            },
            'relative_sensitivity': {
                'temperature': temp_rel_sens,
                'velocity': vel_rel_sens,
                'efficiency': eff_rel_sens
            },
            'maximum_sensitivity': {
                'temperature': max_temp_sens,
                'velocity': max_vel_sens,
                'efficiency': max_eff_sens
            },
            'ranges': {
                'temperature': {
                    'min': min(temperatures),
                    'max': max(temperatures),
                    'span': max(temperatures) - min(temperatures)
                },
                'velocity': {
                    'min': min(velocities),
                    'max': max(velocities),
                    'span': max(velocities) - min(velocities)
                },
                'pressure_drop': {
                    'min': min(pressure_drops),
                    'max': max(pressure_drops),
                    'span': max(pressure_drops) - min(pressure_drops)
                },
                'efficiency': {
                    'min': min(efficiencies),
                    'max': max(efficiencies),
                    'span': max(efficiencies) - min(efficiencies)
                }
            }
        }

    def _rank_sensitivity(self, analysis_results: Dict) -> List[Dict]:
        """
        Clasificar parámetros por sensibilidad
        """
        ranking = []

        for param, data in analysis_results.items():
            # Calcular índice de sensibilidad compuesto
            max_temp_sens = data['metrics']['maximum_sensitivity']['temperature']
            max_vel_sens = data['metrics']['maximum_sensitivity']['velocity']
            max_eff_sens = data['metrics']['maximum_sensitivity']['efficiency']

            # Índice ponderado
            sensitivity_index = (max_temp_sens * 0.4 +
                                max_vel_sens * 0.3 +
                                max_eff_sens * 0.3)

            ranking.append({
                'parameter': param,
                'sensitivity_index': sensitivity_index,
                'max_temp_sens': max_temp_sens,
                'max_vel_sens': max_vel_sens,
                'max_eff_sens': max_eff_sens
            })

        # Ordenar por sensibilidad (mayor a menor)
        ranking.sort(key=lambda x: x['sensitivity_index'], reverse=True)

        return ranking

    def _generate_recommendations(self, analysis_results: Dict) -> List[str]:
        """
        Generar recomendaciones basadas en análisis
        """
        recommendations = []
        ranking = self._rank_sensitivity(analysis_results)

        # Top 3 parámetros más sensibles
        for i, item in enumerate(ranking[:3]):
            param = item['parameter']
            sens = item['sensitivity_index']

            if param == 'excess_air':
                if sens > 20:
                    recommendations.append(
                        f"El aire en exceso es ALTAMENTE sensible ({sens:.1f}%). "
                        "Considere control preciso de la relación aire-combustible."
                    )
                elif sens > 10:
                    recommendations.append(
                        f"El aire en exceso es moderadamente sensible ({sens:.1f}%). "
                        "Mantenga control estadístico del proceso."
                    )

            elif param == 'furnace_efficiency':
                if sens > 15:
                    recommendations.append(
                        f"La eficiencia del horno impacta significativamente ({sens:.1f}%). "
                        "Programar mantenimiento preventivo regular."
                    )

            elif param == 'moisture':
                if sens > 25:
                    recommendations.append(
                        f"La humedad del combustible es CRÍTICA ({sens:.1f}%). "
                        "Implementar sistema de secado o control de calidad."
                    )

            elif param == 'flow_rate':
                if sens > 30:
                    recommendations.append(
                        f"El flujo de biomasa es muy sensible ({sens:.1f}%). "
                        "Instalar medidores de flujo calibrados y control PID."
                    )

        # Recomendación general
        if not recommendations:
            recommendations.append(
                "El sistema muestra buena estabilidad. Mantener condiciones operativas actuales."
            )

        return recommendations

    def _get_parameter_unit(self, parameter_name: str) -> str:
        """
        Obtener unidad del parámetro
        """
        units = {
            'flow_rate': 'ton/hora',
            'reported_PCI': 'kJ/kg',
            'furnace_efficiency': '%',
            'excess_air': '%',
            'duct_diameter': 'pulgadas',
            'carbon': '%',
            'hydrogen': '%',
            'oxygen': '%',
            'nitrogen': '%',
            'sulfur': '%',
            'ash': '%',
            'moisture': '%',
            'relative_humidity': '%',
            'dry_bulb_temp': '°C',
            'altitude': 'm'
        }

        return units.get(parameter_name, '')

    def optimize_parameter(self, parameter_name: str,
                          objective: str = 'efficiency',
                          constraints: Dict = None) -> Dict:
        """
        Optimizar un parámetro para un objetivo específico
        """
        if constraints is None:
            constraints = {}

        # Rango de búsqueda
        base_value = getattr(self.base_input, parameter_name)
        search_range = constraints.get('range', 50)  # 50% por defecto
        min_val = constraints.get('min', base_value * (1 - search_range/100))
        max_val = constraints.get('max', base_value * (1 + search_range/100))

        # Búsqueda simple (grid search)
        n_points = 100
        values = np.linspace(min_val, max_val, n_points)
        best_value = base_value
        best_score = float('-inf')

        for value in values:
            setattr(self.base_input, parameter_name, value)
            results = self.calculator.calculate_all()

            # Evaluar objetivo
            if objective == 'efficiency':
                score = results.real_efficiency
            elif objective == 'temperature':
                score = -abs(results.outlet_gas_temp - 1273)  # Target 1000°C
            elif objective == 'velocity':
                score = -abs(results.gas_velocity - 15)  # Target 15 m/s
            else:
                score = results.real_efficiency

            # Verificar restricciones
            valid = True
            if 'max_velocity' in constraints:
                if results.gas_velocity > constraints['max_velocity']:
                    valid = False
            if 'min_efficiency' in constraints:
                if results.real_efficiency < constraints['min_efficiency']:
                    valid = False
            if 'max_temp' in constraints:
                if results.outlet_gas_temp > constraints['max_temp']:
                    valid = False

            if valid and score > best_score:
                best_score = score
                best_value = value

        # Restaurar valor original
        setattr(self.base_input, parameter_name, base_value)

        # Calcular resultados óptimos
        setattr(self.base_input, parameter_name, best_value)
        optimal_results = self.calculator.calculate_all()
        setattr(self.base_input, parameter_name, base_value)

        return {
            'parameter': parameter_name,
            'optimal_value': best_value,
            'original_value': base_value,
            'improvement': best_score - getattr(self.calculator.calculate_all(), objective),
            'results': optimal_results
        }