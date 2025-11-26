"""
Motor principal de cálculos termodinámicos de combustión de biomasa
Implementa los 38 cálculos requeridos
"""

from typing import Dict, List, Tuple
import numpy as np
from scipy.optimize import fsolve
from ..models.biomass import BiomassInput
from ..models.results import CombustionResults, SensibilityResults
from ..utils.constants import *
from ..utils.equations import *


class CombustionCalculator:
    """Clase principal para cálculos de combustión de biomasa"""

    def __init__(self, input_data: BiomassInput):
        self.input = input_data
        self.results = {}

    def calculate_all(self) -> CombustionResults:
        """
        Ejecutar todos los cálculos (38 cálculos totales)
        """
        # Grupo 1: Propiedades del combustible (1-6)
        self._calculate_fuel_properties()

        # Grupo 2: Propiedades del aire (7-9)
        self._calculate_air_properties()

        # Grupo 3: Estequiometría (10-12)
        self._calculate_stoichiometry()

        # Grupo 4: Balance de masa (13-14)
        self._calculate_mass_balance()

        # Grupo 5: Balance de energía (15-18)
        self._calculate_energy_balance()

        # Grupo 6: Dinámica de fluidos (19-26)
        self._calculate_fluid_dynamics()

        # Grupo 7: Transferencia de calor (27-32)
        self._calculate_heat_transfer()

        # Grupo 8: Emisiones (33-35)
        self._calculate_emissions()

        return self._compile_results()

    def _calculate_fuel_properties(self):
        """Cálculos 1-6: Propiedades del combustible"""
        # 1. Composición en base húmeda
        moisture_factor = (100 - self.input.moisture) / 100
        self.results['composition_wet'] = {
            'C': self.input.carbon * moisture_factor,
            'H': self.input.hydrogen * moisture_factor,
            'O': self.input.oxygen * moisture_factor,
            'N': self.input.nitrogen * moisture_factor,
            'S': self.input.sulfur * moisture_factor,
            'ash': self.input.ash * moisture_factor,
            'H2O': self.input.moisture
        }

        # 2 y 3. PCS y PCI (fórmula de Dulong)
        heating_values = dulong_heating_value(
            self.input.carbon,
            self.input.hydrogen,
            self.input.oxygen,
            self.input.sulfur,
            self.input.ash,
            self.input.moisture
        )
        self.results['PCS'] = heating_values['PCS']
        self.results['PCI_calculated'] = heating_values['PCI']

        # 4. Relación aire/combustible teórica
        self.results['theoretical_air'] = theoretical_air_fuel_ratio(
            self.input.carbon,
            self.input.hydrogen,
            self.input.oxygen,
            self.input.sulfur
        )

        # 5. Aire real con exceso
        self.results['real_air'] = self.results['theoretical_air'] * \
                                  (1 + self.input.excess_air / 100)

        # 6. Agua en combustión
        self.results['water_combustion'] = heating_values['water_from_combustion']

    def _calculate_air_properties(self):
        """Cálculos 7-9: Propiedades del aire"""
        # 7. Presión atmosférica a altitud
        self.results['atmospheric_pressure'] = pressure_altitude(
            self.input.altitude
        )  # kPa

        # 8. Densidad del aire
        temp_k = self.input.dry_bulb_temp + 273.15
        pressure_pa = self.results['atmospheric_pressure'] * 1000
        self.results['air_density'] = pressure_pa / (R_AIR * temp_k)

        # 9. Humedad absoluta y entalpía del aire
        self.results['absolute_humidity'] = absolute_humidity(
            self.input.relative_humidity,
            self.input.dry_bulb_temp,
            self.results['atmospheric_pressure']
        )
        self.results['air_enthalpy'] = moist_air_enthalpy(
            self.input.dry_bulb_temp,
            self.results['absolute_humidity']
        )

    def _calculate_stoichiometry(self):
        """Cálculos 10-12: Estequiometría de combustión"""
        products = combustion_products(
            self.input.carbon,
            self.input.hydrogen,
            self.input.sulfur,
            self.input.moisture,
            self.input.ash,
            self.input.excess_air
        )

        # Guardar productos de combustión
        self.results['products'] = products

        # 10-12. Fracciones másicas de productos
        self.results['CO2_mass'] = products['CO2']
        self.results['H2O_mass'] = products['H2O']
        self.results['SO2_mass'] = products['SO2']
        self.results['O2_excess'] = products['O2']
        self.results['N2_mass'] = products['N2']

    def _calculate_mass_balance(self):
        """Cálculos 13-14: Balance de masa"""
        # 13. Flujo másico de combustible
        self.results['flow_rate_kg_s'] = self.input.flow_rate * \
                                        CONVERSION_FACTORS['ton_to_kg'] / \
                                        CONVERSION_FACTORS['hour_to_sec']

        # 14. Flujo másico total de gases
        self.results['total_gas_mass'] = self.results['products']['total_gases']
        self.results['mass_flow_gases'] = self.results['flow_rate_kg_s'] * \
                                          (1 + self.results['real_air'])

    def _calculate_energy_balance(self):
        """Cálculos 15-18: Balance de energía"""
        # 15. Energía total liberada
        self.results['total_energy'] = self.results['flow_rate_kg_s'] * \
                                      self.input.reported_PCI  # kW

        # 16. Energía útil (considerando eficiencia)
        self.results['useful_energy'] = self.results['total_energy'] * \
                                       (self.input.furnace_efficiency / 100)

        # 17. Temperatura adiabática de llama (iteración)
        self.results['adiabatic_temp'] = self._calculate_adiabatic_temperature()

        # 18. Temperatura de salida
        # Simplificación: T_salida = T_ambient + (Q_util/(m_gases * Cp_promedio))
        Cp_avg = 1.1  # kJ/(kg·K) valor típico para gases de combustión
        temp_rise = self.results['useful_energy'] / \
                   (self.results['mass_flow_gases'] * Cp_avg)
        self.results['outlet_temp'] = self.input.dry_bulb_temp + temp_rise

        # 19. Eficiencia real
        self.results['real_efficiency'] = self.input.furnace_efficiency
        self.results['chimney_losses'] = self.results['total_energy'] - \
                                         self.results['useful_energy']

    def _calculate_adiabatic_temperature(self) -> float:
        """
        Calcular temperatura adiabática usando método iterativo
        """
        T_guess = 2000  # K

        def energy_balance(T):
            # Calor de combustión
            Q_comb = self.results['PCI_calculated'] * 1000  # J/kg

            # Calor absorbido por productos
            Cp_CO2 = 0.844 * (T - 298) * self.results['CO2_mass']
            Cp_H2O = 1.86 * (T - 298) * self.results['H2O_mass']
            Cp_O2 = 0.918 * (T - 298) * self.results['O2_excess']
            Cp_N2 = 1.04 * (T - 298) * self.results['N2_mass']
            Cp_SO2 = 0.64 * (T - 298) * self.results['SO2_mass']

            Q_absorbed = Cp_CO2 + Cp_H2O + Cp_O2 + Cp_N2 + Cp_SO2
            return Q_comb - Q_absorbed

        # Resolver con scipy
        T_adiabatic = fsolve(energy_balance, T_guess)[0]
        return max(T_adiabatic, 298)  # Mínimo temperatura ambiente

    def _calculate_fluid_dynamics(self):
        """Cálculos 20-26: Dinámica de fluidos"""
        # 20. Densidad de gases de combustión
        temp_avg_k = (self.results['outlet_temp'] + self.input.dry_bulb_temp) / 2 + 273.15
        pressure_pa = self.results['atmospheric_pressure'] * 1000

        # Composición para densidad
        gas_composition = {
            'CO2': self.results['CO2_mass'],
            'H2O': self.results['H2O_mass'],
            'SO2': self.results['SO2_mass'],
            'O2': self.results['O2_excess'],
            'N2': self.results['N2_mass']
        }
        self.results['gas_density'] = gas_density(temp_avg_k, pressure_pa,
                                                 gas_composition)

        # 21. Flujo volumétrico
        self.results['volumetric_flow'] = self.results['mass_flow_gases'] / \
                                         self.results['gas_density']

        # 22. Área del ducto
        diameter_m = self.input.duct_diameter * CONVERSION_FACTORS['inch_to_m']
        self.results['duct_area'] = math.pi * (diameter_m ** 2) / 4

        # 23. Velocidad de gases
        self.results['gas_velocity'] = self.results['volumetric_flow'] / \
                                      self.results['duct_area']

        # 24. Número de Reynolds
        self.results['reynolds'] = reynolds_number(
            self.results['gas_velocity'],
            diameter_m,
            self.results['gas_density']
        )

        # 25. Factor de fricción (Colebrook)
        self.results['friction_factor'] = colebrook_friction_factor(
            self.results['reynolds'],
            diameter_m,
            REFRACTORY_PROPERTIES['roughness']
        )

        # 26. Caída de presión por metro
        self.results['pressure_drop'] = pressure_drop_per_length(
            self.results['friction_factor'],
            self.results['gas_density'],
            self.results['gas_velocity'],
            diameter_m
        )

    def _calculate_heat_transfer(self):
        """Cálculos 27-32: Transferencia de calor"""
        diameter_m = self.input.duct_diameter * CONVERSION_FACTORS['inch_to_m']

        # 27-28. Resistencia térmica y coeficiente U
        # Simplificación: conducción + convección
        h_internal = 50  # W/(m²·K) - coeficiente convección interno
        h_external = 10  # W/(m²·K) - coeficiente convección externo

        R_convection_int = 1 / (h_internal * math.pi * diameter_m)
        R_conduction = math.log((diameter_m/2 + REFRACTORY_PROPERTIES['thickness']) /
                               (diameter_m/2)) / (2 * math.pi *
                                                 REFRACTORY_PROPERTIES['thermal_conductivity'])
        R_convection_ext = 1 / (h_external * math.pi *
                               (diameter_m + 2 * REFRACTORY_PROPERTIES['thickness']))

        self.results['thermal_resistance'] = R_convection_int + R_conduction + R_convection_ext
        self.results['heat_transfer_coefficient'] = 1 / self.results['thermal_resistance']

        # 29. Pérdida de calor por metro
        delta_T = self.results['outlet_temp'] - self.input.dry_bulb_temp
        self.results['heat_loss_per_meter'] = self.results['heat_transfer_coefficient'] * \
                                             delta_T

        # 30. Temperatura de pared externa
        self.results['external_wall_temp'] = self.input.dry_bulb_temp + \
                                            (self.results['heat_loss_per_meter'] *
                                             R_convection_ext)

        # 31. Gradiente en refractario
        self.results['refractory_gradient'] = self.results['heat_loss_per_meter'] * \
                                             R_conduction

        # 32. Eficiencia de aislamiento
        heat_loss_no_insulation = h_external * math.pi * diameter_m * delta_T
        self.results['insulation_efficiency'] = \
            (heat_loss_no_insulation - self.results['heat_loss_per_meter']) / \
            heat_loss_no_insulation * 100

    def _calculate_emissions(self):
        """Cálculos 33-35: Emisiones"""
        # 33. Factor de emisión de CO₂
        self.results['co2_emission_factor'] = 44/12 * \
                                             self.results['composition_wet']['C'] / 100

        # 34. Concentración de CO₂ en gases secos
        dry_gases = (self.results['CO2_mass'] + self.results['O2_excess'] +
                    self.results['N2_mass'] + self.results['SO2_mass'])
        if dry_gases > 0:
            self.results['co2_concentration_dry'] = \
                self.results['CO2_mass'] / dry_gases * 100
        else:
            self.results['co2_concentration_dry'] = 0

        # 35. Poder calorífico volumétrico
        fuel_density = 1200  # kg/m³ (densidad típica bagazo)
        self.results['volumetric_heating_value'] = \
            self.results['PCI_calculated'] * fuel_density

    def _compile_results(self) -> CombustionResults:
        """Compilar todos los resultados en el modelo de salida"""
        # Calcular fracciones volumétricas (simplificado)
        total_vol = (self.results['CO2_mass'] / GAS_PROPERTIES['CO2']['molar_mass'] +
                    self.results['H2O_mass'] / GAS_PROPERTIES['H2O']['molar_mass'] +
                    self.results['O2_excess'] / GAS_PROPERTIES['O2']['molar_mass'] +
                    self.results['N2_mass'] / GAS_PROPERTIES['N2']['molar_mass'] +
                    self.results['SO2_mass'] / GAS_PROPERTIES['SO2']['molar_mass'])

        if total_vol > 0:
            co2_vol = (self.results['CO2_mass'] / GAS_PROPERTIES['CO2']['molar_mass']) / total_vol * 100
            h2o_vol = (self.results['H2O_mass'] / GAS_PROPERTIES['H2O']['molar_mass']) / total_vol * 100
            so2_vol = (self.results['SO2_mass'] / GAS_PROPERTIES['SO2']['molar_mass']) / total_vol * 100
            o2_vol = (self.results['O2_excess'] / GAS_PROPERTIES['O2']['molar_mass']) / total_vol * 100
            n2_vol = (self.results['N2_mass'] / GAS_PROPERTIES['N2']['molar_mass']) / total_vol * 100
        else:
            co2_vol = h2o_vol = so2_vol = o2_vol = n2_vol = 0

        return CombustionResults(
            # Propiedades combustible
            pcs=self.results['PCS'],
            pci_calculated=self.results['PCI_calculated'],
            composition_wet_base=self.results['composition_wet'],

            # Propiedades aire
            air_density=self.results['air_density'],
            absolute_humidity=self.results['absolute_humidity'],
            air_enthalpy=self.results['air_enthalpy'],

            # Estequiometría
            theoretical_air=self.results['theoretical_air'],
            real_air=self.results['real_air'],
            excess_air_percentage=self.input.excess_air,

            # Productos
            co2=self.results['CO2_mass'],
            h2o=self.results['H2O_mass'],
            so2=self.results['SO2_mass'],
            o2_excess=self.results['O2_excess'],
            n2=self.results['N2_mass'],
            total_gas_mass=self.results['total_gas_mass'],

            # Fracciones volumétricas
            co2_fraction_vol=co2_vol,
            h2o_fraction_vol=h2o_vol,
            so2_fraction_vol=so2_vol,
            o2_fraction_vol=o2_vol,
            n2_fraction_vol=n2_vol,

            # Energía
            total_energy_released=self.results['total_energy'] / 1000,  # MW
            useful_energy=self.results['useful_energy'] / 1000,  # MW
            adiabatic_flame_temp=self.results['adiabatic_temp'],
            outlet_gas_temp=self.results['outlet_temp'],
            chimney_losses=self.results['chimney_losses'] / 1000,  # MW
            real_efficiency=self.results['real_efficiency'],

            # Dinámica
            gas_density=self.results['gas_density'],
            volumetric_flow=self.results['volumetric_flow'],
            duct_area=self.results['duct_area'],
            gas_velocity=self.results['gas_velocity'],
            reynolds_number=self.results['reynolds'],
            friction_factor=self.results['friction_factor'],
            pressure_drop=self.results['pressure_drop'],

            # Transferencia de calor
            thermal_resistance=self.results['thermal_resistance'],
            heat_transfer_coefficient=self.results['heat_transfer_coefficient'],
            heat_loss_per_meter=self.results['heat_loss_per_meter'],
            external_wall_temp=self.results['external_wall_temp'],
            refractory_gradient=self.results['refractory_gradient'],
            insulation_efficiency=self.results['insulation_efficiency'],

            # Emisiones
            co2_emission_factor=self.results['co2_emission_factor'],
            co2_concentration_dry=self.results['co2_concentration_dry'],
            volumetric_heating_value=self.results['volumetric_heating_value'],

            # Propiedades adicionales
            flow_rate_kg_s=self.results['flow_rate_kg_s'],
            mass_flow_gases=self.results['mass_flow_gases']
        )

    def sensitivity_analysis(self, parameter_name: str,
                           parameter_values: List[float]) -> SensibilityResults:
        """
        Realizar análisis de sensibilidad para un parámetro
        """
        temperatures = []
        velocities = []
        pressure_drops = []
        efficiencies = []

        # Valor original del parámetro
        original_value = getattr(self.input, parameter_name)

        for value in parameter_values:
            # Modificar el parámetro
            setattr(self.input, parameter_name, value)

            # Recalcular
            results = self.calculate_all()

            # Guardar resultados
            temperatures.append(results.outlet_gas_temp - 273.15)  # °C
            velocities.append(results.gas_velocity)
            pressure_drops.append(results.pressure_drop)
            efficiencies.append(results.real_efficiency)

        # Restaurar valor original
        setattr(self.input, parameter_name, original_value)

        return SensibilityResults(
            parameter_name=parameter_name,
            parameter_values=parameter_values,
            temperatures=temperatures,
            velocities=velocities,
            pressure_drops=pressure_drops,
            efficiencies=efficiencies
        )