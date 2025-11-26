"""
Tests para validar los cálculos de combustión
DML Ingenieros Consultores
"""

import pytest
import sys
import os

# Agregar el path del backend al sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.models.biomass import BiomassInput
from app.services.combustion import CombustionCalculator


class TestCombustionCalculator:
    """Suite de tests para el calculador de combustión"""

    def test_basic_input_validation(self):
        """Test de validación de entrada básica"""
        # Input válido
        input_data = BiomassInput(
            project_code="TEST-001",
            document_code="DOC-001",
            analyst="Test Analyst",
            carbon=50.29,
            hydrogen=5.82,
            oxygen=42.94,
            nitrogen=0.22,
            sulfur=0.08,
            ash=0.66,
            moisture=35.09
        )
        assert input_data is not None

    def test_combustion_calculator_initialization(self):
        """Test de inicialización del calculador"""
        input_data = BiomassInput(
            project_code="TEST-001",
            document_code="DOC-001",
            analyst="Test Analyst",
            carbon=50.29,
            hydrogen=5.82,
            oxygen=42.94,
            nitrogen=0.22,
            sulfur=0.08,
            ash=0.66,
            moisture=35.09,
            flow_rate=3000,
            reported_PCI=11367,
            furnace_efficiency=90,
            excess_air=30,
            duct_diameter=30
        )

        calculator = CombustionCalculator(input_data)
        assert calculator is not None
        assert calculator.input == input_data

    def test_fuel_properties_calculation(self):
        """Test de cálculo de propiedades del combustible"""
        input_data = BiomassInput(
            project_code="TEST-001",
            document_code="DOC-001",
            analyst="Test Analyst",
            carbon=50.29,
            hydrogen=5.82,
            oxygen=42.94,
            nitrogen=0.22,
            sulfur=0.08,
            ash=0.66,
            moisture=35.09
        )

        calculator = CombustionCalculator(input_data)
        calculator._calculate_fuel_properties()

        # Verificar PCS y PCI calculados
        assert 'PCS' in calculator.results
        assert 'PCI_calculated' in calculator.results
        assert calculator.results['PCS'] > 0
        assert calculator.results['PCI_calculated'] > 0
        assert calculator.results['PCS'] > calculator.results['PCI_calculated']

    def test_stoichiometry_calculation(self):
        """Test de cálculos estequiométricos"""
        input_data = BiomassInput(
            project_code="TEST-001",
            document_code="DOC-001",
            analyst="Test Analyst",
            carbon=50.29,
            hydrogen=5.82,
            oxygen=42.94,
            nitrogen=0.22,
            sulfur=0.08,
            ash=0.66,
            moisture=35.09,
            excess_air=30
        )

        calculator = CombustionCalculator(input_data)
        calculator._calculate_fuel_properties()
        calculator._calculate_stoichiometry()

        # Verificar productos de combustión
        assert 'products' in calculator.results
        products = calculator.results['products']

        assert products['CO2'] > 0
        assert products['H2O'] > 0
        assert products['SO2'] >= 0
        assert products['O2_excess'] > 0
        assert products['N2'] > 0

    def test_energy_balance(self):
        """Test de balance de energía"""
        input_data = BiomassInput(
            project_code="TEST-001",
            document_code="DOC-001",
            analyst="Test Analyst",
            carbon=50.29,
            hydrogen=5.82,
            oxygen=42.94,
            nitrogen=0.22,
            sulfur=0.08,
            ash=0.66,
            moisture=35.09,
            flow_rate=3000,
            reported_PCI=11367,
            furnace_efficiency=90,
            excess_air=30
        )

        calculator = CombustionCalculator(input_data)
        calculator._calculate_fuel_properties()
        calculator._calculate_stoichiometry()
        calculator._calculate_mass_balance()
        calculator._calculate_energy_balance()

        # Verificar balance de energía
        assert 'total_energy' in calculator.results
        assert 'useful_energy' in calculator.results
        assert 'real_efficiency' in calculator.results

        # La energía útil debe ser menor que la total
        assert calculator.results['useful_energy'] < calculator.results['total_energy']

        # La eficiencia debe ser igual a la especificada (en este test)
        assert abs(calculator.results['real_efficiency'] - 90) < 0.1

    def test_fluid_dynamics(self):
        """Test de cálculos de dinámica de fluidos"""
        input_data = BiomassInput(
            project_code="TEST-001",
            document_code="DOC-001",
            analyst="Test Analyst",
            carbon=50.29,
            hydrogen=5.82,
            oxygen=42.94,
            nitrogen=0.22,
            sulfur=0.08,
            ash=0.66,
            moisture=35.09,
            flow_rate=3000,
            reported_PCI=11367,
            furnace_efficiency=90,
            excess_air=30,
            duct_diameter=30
        )

        calculator = CombustionCalculator(input_data)
        results = calculator.calculate_all()

        # Verificar parámetros de fluidos
        assert results.gas_density > 0
        assert results.volumetric_flow > 0
        assert results.gas_velocity > 0
        assert results.reynolds_number > 0
        assert results.pressure_drop > 0

        # Verificar rangos razonables
        assert 0.5 < results.gas_density < 2.0  # kg/m³
        assert 5 < results.gas_velocity < 25      # m/s
        assert results.reynolds_number > 2300     # Flujo turbulento

    def test_complete_calculation(self):
        """Test completo del cálculo con datos conocidos"""
        input_data = BiomassInput(
            project_code="TEST-BAGAZO",
            document_code="DML-TEST",
            analyst="Engineer Test",
            city="Bogotá",
            altitude=2640,
            relative_humidity=75,
            dry_bulb_temp=15,
            biomass_type="Bagazo de caña",
            flow_rate=3000,
            carbon=50.29,
            hydrogen=5.82,
            oxygen=42.94,
            nitrogen=0.22,
            sulfur=0.08,
            ash=0.66,
            moisture=35.09,
            reported_PCI=11367,
            furnace_efficiency=90,
            excess_air=30,
            duct_diameter=30
        )

        calculator = CombustionCalculator(input_data)
        results = calculator.calculate_all()

        # Verificar todos los resultados principales
        assert results.pcs > 0
        assert results.pci_calculated > 0
        assert results.adiabatic_flame_temp > 1000  # K
        assert results.outlet_gas_temp > 500       # K
        assert results.real_efficiency > 0
        assert results.real_efficiency <= 100

        # Verificar composición de gases
        total_vol_fraction = (results.co2_fraction_vol +
                             results.h2o_fraction_vol +
                             results.o2_fraction_vol +
                             results.n2_fraction_vol +
                             results.so2_fraction_vol)
        assert abs(total_vol_fraction - 100) < 1  # Debe sumar aproximadamente 100%

    def test_extreme_values(self):
        """Test con valores extremos para robustez"""
        # Test con aire en exceso muy alto
        input_data = BiomassInput(
            project_code="EXTREME-TEST",
            document_code="DOC-001",
            analyst="Test",
            carbon=50.29,
            hydrogen=5.82,
            oxygen=42.94,
            nitrogen=0.22,
            sulfur=0.08,
            ash=0.66,
            moisture=35.09,
            excess_air=100  # 100% de aire en exceso
        )

        calculator = CombustionCalculator(input_data)
        results = calculator.calculate_all()

        # Debe manejar valores extremos sin errores
        assert results is not None
        assert results.gas_velocity > 0
        assert results.o2_fraction_vol > 10  # Más oxígeno por exceso

    def test_biomass_types(self):
        """Test con diferentes tipos de biomasa"""
        biomass_configs = [
            {
                'name': 'Madera',
                'carbon': 49.5,
                'hydrogen': 6.1,
                'oxygen': 43.8,
                'nitrogen': 0.2,
                'sulfur': 0.0,
                'ash': 0.4
            },
            {
                'name': 'Cascarilla',
                'carbon': 33.6,
                'hydrogen': 5.1,
                'oxygen': 38.8,
                'nitrogen': 0.5,
                'sulfur': 0.1,
                'ash': 21.9
            }
        ]

        for config in biomass_configs:
            input_data = BiomassInput(
                project_code=f"TEST-{config['name']}",
                document_code="DOC-001",
                analyst="Test",
                **config,
                moisture=15.0,
                flow_rate=1000
            )

            calculator = CombustionCalculator(input_data)
            results = calculator.calculate_all()

            assert results is not None
            assert results.pcs > 0
            print(f"✅ {config['name']} calculado correctamente")

    def test_sensitivity_analysis(self):
        """Test de análisis de sensibilidad"""
        input_data = BiomassInput(
            project_code="SENSITIVITY-TEST",
            document_code="DOC-001",
            analyst="Test",
            carbon=50.29,
            hydrogen=5.82,
            oxygen=42.94,
            nitrogen=0.22,
            sulfur=0.08,
            ash=0.66,
            moisture=35.09,
            flow_rate=3000
        )

        calculator = CombustionCalculator(input_data)

        # Test sensibilidad para aire en exceso
        param_values = [10, 20, 30, 40, 50]
        results = calculator.sensitivity_analysis('excess_air', param_values)

        assert results.parameter_name == 'excess_air'
        assert len(results.parameter_values) == 5
        assert len(results.temperatures) == 5
        assert len(results.velocities) == 5

        # La temperatura debe disminuir con más aire en exceso
        assert results.temperatures[-1] < results.temperatures[0]

    def test_edge_cases(self):
        """Test de casos extremos y límites"""
        # Test con valores mínimos
        input_data_min = BiomassInput(
            project_code="MIN-TEST",
            document_code="DOC-001",
            analyst="Test",
            carbon=1.0,
            hydrogen=0.1,
            oxygen=0.1,
            nitrogen=0.0,
            sulfur=0.0,
            ash=98.8,
            moisture=5.0,
            flow_rate=1
        )

        calculator = CombustionCalculator(input_data_min)
        results_min = calculator.calculate_all()
        assert results_min is not None

        # Test con valores máximos
        input_data_max = BiomassInput(
            project_code="MAX-TEST",
            document_code="DOC-001",
            analyst="Test",
            carbon=95.0,
            hydrogen=5.0,
            oxygen=0.0,
            nitrogen=0.0,
            sulfur=0.0,
            ash=0.0,
            moisture=0.0,
            flow_rate=10000
        )

        calculator = CombustionCalculator(input_data_max)
        results_max = calculator.calculate_all()
        assert results_max is not None


if __name__ == '__main__':
    # Ejecutar tests
    print("🔬 Ejecutando tests del Sistema de Cálculo Energético...")
    print("=" * 60)

    # Crear instancia de tests
    test_instance = TestCombustionCalculator()

    # Lista de métodos de test
    test_methods = [
        ('Validación de Entrada', test_instance.test_basic_input_validation),
        ('Inicialización', test_instance.test_combustion_calculator_initialization),
        ('Propiedades del Combustible', test_instance.test_fuel_properties_calculation),
        ('Estequiometría', test_instance.test_stoichiometry_calculation),
        ('Balance de Energía', test_instance.test_energy_balance),
        ('Dinámica de Fluidos', test_instance.test_fluid_dynamics),
        ('Cálculo Completo', test_instance.test_complete_calculation),
        ('Valores Extremos', test_instance.test_extreme_values),
        ('Tipos de Biomasa', test_instance.test_biomass_types),
        ('Análisis de Sensibilidad', test_instance.test_sensitivity_analysis),
        ('Casos Límite', test_instance.test_edge_cases)
    ]

    # Ejecutar tests
    passed = 0
    failed = 0

    for test_name, test_method in test_methods:
        try:
            test_method()
            print(f"✅ {test_name}: PASADO")
            passed += 1
        except Exception as e:
            print(f"❌ {test_name}: FALLIDO - {str(e)}")
            failed += 1

    print("=" * 60)
    print(f"\n📊 Resultados:")
    print(f"   Pasados: {passed}")
    print(f"   Fallidos: {failed}")
    print(f"   Total:   {passed + failed}")

    if failed == 0:
        print("\n🎉 Todos los tests pasaron exitosamente!")
        exit(0)
    else:
        print(f"\n⚠️ {failed} tests fallaron. Revisar los errores.")
        exit(1)