// Aplicación principal para Sistema de Cálculo Energético de Biomasa
// DML Ingenieros Consultores

// Estado global de la aplicación
const appState = {
    currentData: null,
    results: null,
    isLoading: false,
    apiBase: 'http://localhost:8000/api' // Cambiar en producción
};

// Inicialización cuando el DOM está listo
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Cargar valores por defecto
    loadDefaults();

    // Configurar event listeners
    setupEventListeners();

    // Cargar condiciones iniciales
    updateCityConditions();

    console.log('✅ Aplicación inicializada');
}

function setupEventListeners() {
    // Validar composición elemental cuando cambia
    const compositionInputs = ['carbon', 'hydrogen', 'oxygen', 'nitrogen', 'sulfur', 'ash'];
    compositionInputs.forEach(id => {
        const input = document.getElementById(id);
        if (input) {
            input.addEventListener('change', validateComposition);
        }
    });

    // Validar rangos
    document.getElementById('furnaceEfficiency').addEventListener('change', function() {
        const value = parseFloat(this.value);
        if (value < 10 || value > 100) {
            showNotification('La eficiencia debe estar entre 10% y 100%', 'warning');
        }
    });

    document.getElementById('moisture').addEventListener('change', function() {
        const value = parseFloat(this.value);
        if (value > 60) {
            showNotification('La humedad no puede superar el 60%', 'warning');
        }
    });
}

function showTab(tabName) {
    // Ocultar todos los tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
        tab.classList.add('hidden');
    });

    // Desactivar todos los botones
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active', 'border-dml-green-500', 'text-dml-green-600');
        btn.classList.add('border-transparent', 'text-gray-500');
    });

    // Mostrar tab seleccionado
    const selectedTab = document.getElementById(`${tabName}-tab`);
    if (selectedTab) {
        selectedTab.classList.remove('hidden');
        setTimeout(() => selectedTab.classList.add('active'), 10);
    }

    // Activar botón seleccionado
    const activeBtn = document.querySelector(`[data-tab="${tabName}"]`);
    if (activeBtn) {
        activeBtn.classList.remove('border-transparent', 'text-gray-500');
        activeBtn.classList.add('active', 'border-dml-green-500', 'text-dml-green-600');
    }
}

async function updateCityConditions() {
    const citySelect = document.getElementById('city');
    if (!citySelect) return;

    const selectedCity = citySelect.value;

    try {
        const response = await fetch(`${appState.apiBase}/city/${selectedCity}`);
        if (response.ok) {
            const conditions = await response.json();

            // Actualizar campos del formulario
            document.getElementById('altitude').value = conditions.altitude;
            document.getElementById('dryBulbTemp').value = conditions.avg_temp;
            document.getElementById('relativeHumidity').value = conditions.avg_humidity;

            showNotification(`Condiciones de ${selectedCity} cargadas`, 'success');
        }
    } catch (error) {
        console.error('Error cargando condiciones de la ciudad:', error);
    }
}

function validateComposition() {
    const carbon = parseFloat(document.getElementById('carbon').value) || 0;
    const hydrogen = parseFloat(document.getElementById('hydrogen').value) || 0;
    const oxygen = parseFloat(document.getElementById('oxygen').value) || 0;
    const nitrogen = parseFloat(document.getElementById('nitrogen').value) || 0;
    const sulfur = parseFloat(document.getElementById('sulfur').value) || 0;
    const ash = parseFloat(document.getElementById('ash').value) || 0;

    const total = carbon + hydrogen + oxygen + nitrogen + sulfur + ash;

    if (Math.abs(total - 100) > 0.5) {
        showNotification(`La composición debe sumar 100%. Actual: ${total.toFixed(2)}%`, 'error');
        document.getElementById('compositionWarning').textContent =
            `Suma actual: ${total.toFixed(2)}%`;
        document.getElementById('compositionWarning').classList.remove('hidden');
    } else {
        document.getElementById('compositionWarning').classList.add('hidden');
    }
}

function loadDefaults() {
    // Valores por defecto del proyecto
    const defaults = {
        projectCode: 'BIO-2024-001',
        documentCode: 'DML-TECH-001',
        analyst: '',
        city: 'Bogotá',
        biomassType: 'Bagazo de caña',
        flowRate: 3000,
        reportedPCI: 11367,
        furnaceEfficiency: 90,
        excessAir: 30,
        ductDiameter: 30,
        carbon: 50.29,
        hydrogen: 5.82,
        oxygen: 42.94,
        nitrogen: 0.22,
        sulfur: 0.08,
        ash: 0.66,
        moisture: 35.09
    };

    // Aplicar valores por defecto
    Object.entries(defaults).forEach(([key, value]) => {
        const element = document.getElementById(key);
        if (element && !element.value) {
            element.value = value;
        }
    });

    showNotification('Valores por defecto cargados', 'info');
}

function resetForm() {
    if (confirm('¿Está seguro de resetear todos los valores?')) {
        document.getElementById('calculationForm').reset();
        loadDefaults();
        hideResults();
        showNotification('Formulario reseteado', 'info');
    }
}

async function calculate() {
    if (appState.isLoading) return;

    // Validar composición
    const compositionValid = validateComposition();
    if (!compositionValid) {
        showNotification('Corrija los errores antes de continuar', 'error');
        return;
    }

    // Recopilar datos del formulario
    const inputData = collectFormData();

    // Mostrar indicador de carga
    showLoading(true);

    try {
        // Realizar cálculos
        const response = await fetch(`${appState.apiBase}/calculate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(inputData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Error en los cálculos');
        }

        const results = await response.json();

        // Guardar resultados
        appState.currentData = inputData;
        appState.results = results;

        // Mostrar resultados
        displayResults(results);

        // Crear gráficos
        createCharts(results);

        // Actualizar análisis de sensibilidad
        updateSensitivityAnalysis();

        showNotification('¡Cálculos completados con éxito!', 'success');

    } catch (error) {
        console.error('Error en cálculos:', error);
        showNotification(`Error: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

function collectFormData() {
    return {
        // Datos del proyecto
        project_code: document.getElementById('projectCode').value,
        document_code: document.getElementById('documentCode').value,
        analyst: document.getElementById('analyst').value,

        // Datos ambientales
        city: document.getElementById('city').value,
        altitude: parseFloat(document.getElementById('altitude').value),
        relative_humidity: parseFloat(document.getElementById('relativeHumidity').value),
        dry_bulb_temp: parseFloat(document.getElementById('dryBulbTemp').value),

        // Datos de biomasa
        biomass_type: document.getElementById('biomassType').value,
        flow_rate: parseFloat(document.getElementById('flowRate').value),
        carbon: parseFloat(document.getElementById('carbon').value),
        hydrogen: parseFloat(document.getElementById('hydrogen').value),
        oxygen: parseFloat(document.getElementById('oxygen').value),
        nitrogen: parseFloat(document.getElementById('nitrogen').value),
        sulfur: parseFloat(document.getElementById('sulfur').value),
        ash: parseFloat(document.getElementById('ash').value),
        moisture: parseFloat(document.getElementById('moisture').value),

        // Datos operacionales
        reported_PCI: parseFloat(document.getElementById('reportedPCI').value),
        furnace_efficiency: parseFloat(document.getElementById('furnaceEfficiency').value),
        excess_air: parseFloat(document.getElementById('excessAir').value),
        duct_diameter: parseFloat(document.getElementById('ductDiameter').value)
    };
}

function showLoading(show) {
    appState.isLoading = show;
    const indicator = document.getElementById('loadingIndicator');

    if (show) {
        indicator.classList.remove('hidden');
    } else {
        indicator.classList.add('hidden');
    }
}

function displayResults(results) {
    // Mostrar sección de resultados
    document.getElementById('resultsSection').classList.remove('hidden');

    // Resultados principales
    displayMainResults(results);

    // Composición de gases
    displayGasComposition(results);

    // Dinámica de fluidos
    displayFluidDynamics(results);

    // Tabla detallada
    displayDetailedResults(results);

    // Scroll a resultados
    document.getElementById('resultsSection').scrollIntoView({
        behavior: 'smooth',
        block: 'start'
    });
}

function displayMainResults(results) {
    const mainResults = document.getElementById('mainResults');

    mainResults.innerHTML = `
        <div class="space-y-4">
            <div class="flex justify-between items-center p-3 bg-white/50 rounded-lg">
                <span class="font-medium text-gray-700">Energía Total</span>
                <span class="result-value">${(results.total_energy_released).toFixed(2)} MW</span>
            </div>
            <div class="flex justify-between items-center p-3 bg-white/50 rounded-lg">
                <span class="font-medium text-gray-700">Energía Útil</span>
                <span class="result-value">${(results.useful_energy).toFixed(2)} MW</span>
            </div>
            <div class="flex justify-between items-center p-3 bg-white/50 rounded-lg">
                <span class="font-medium text-gray-700">Eficiencia Real</span>
                <span class="text-2xl font-bold ${results.real_efficiency >= 80 ? 'text-green-600' : 'text-yellow-600'}">
                    ${results.real_efficiency.toFixed(1)}%
                </span>
            </div>
            <div class="flex justify-between items-center p-3 bg-white/50 rounded-lg">
                <span class="font-medium text-gray-700">Temp. Gases Salida</span>
                <span class="text-2xl font-bold text-blue-600">
                    ${(results.outlet_gas_temp - 273.15).toFixed(1)}°C
                </span>
            </div>
        </div>
    `;
}

function displayGasComposition(results) {
    const gasComposition = document.getElementById('gasComposition');

    gasComposition.innerHTML = `
        <div class="space-y-3">
            <div>
                <div class="flex justify-between text-sm mb-1">
                    <span>CO₂</span>
                    <span>${results.co2_fraction_vol.toFixed(1)}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill progress-fill-red"
                         style="width: ${results.co2_fraction_vol}%"></div>
                </div>
            </div>
            <div>
                <div class="flex justify-between text-sm mb-1">
                    <span>H₂O</span>
                    <span>${results.h2o_fraction_vol.toFixed(1)}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill progress-fill-blue"
                         style="width: ${results.h2o_fraction_vol}%"></div>
                </div>
            </div>
            <div>
                <div class="flex justify-between text-sm mb-1">
                    <span>O₂ (exceso)</span>
                    <span>${results.o2_fraction_vol.toFixed(1)}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill progress-fill-yellow"
                         style="width: ${results.o2_fraction_vol}%"></div>
                </div>
            </div>
            <div>
                <div class="flex justify-between text-sm mb-1">
                    <span>N₂</span>
                    <span>${results.n2_fraction_vol.toFixed(1)}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill progress-fill-green"
                         style="width: ${results.n2_fraction_vol}%"></div>
                </div>
            </div>
        </div>
    `;
}

function displayFluidDynamics(results) {
    const fluidDynamics = document.getElementById('fluidDynamics');

    // Evaluar estado de la velocidad
    let velocityClass = 'text-green-600';
    let velocityBadge = 'badge-green';
    if (results.gas_velocity > 15) {
        velocityClass = 'text-red-600';
        velocityBadge = 'badge-red';
    } else if (results.gas_velocity > 10) {
        velocityClass = 'text-yellow-600';
        velocityBadge = 'badge-yellow';
    }

    fluidDynamics.innerHTML = `
        <div class="space-y-4">
            <div class="flex justify-between items-center p-3 bg-white/50 rounded-lg">
                <span class="font-medium text-gray-700">Velocidad Gases</span>
                <div class="text-right">
                    <span class="result-value ${velocityClass}">${results.gas_velocity.toFixed(1)}</span>
                    <span class="text-sm text-gray-600">m/s</span>
                    <span class="badge ${velocityBadge} ml-2">
                        ${results.gas_velocity > 15 ? 'Alta' : results.gas_velocity > 10 ? 'Media' : 'Normal'}
                    </span>
                </div>
            </div>
            <div class="flex justify-between items-center p-3 bg-white/50 rounded-lg">
                <span class="font-medium text-gray-700">Caída de Presión</span>
                <span class="text-2xl font-bold text-orange-600">
                    ${results.pressure_drop.toFixed(1)} Pa/m
                </span>
            </div>
            <div class="flex justify-between items-center p-3 bg-white/50 rounded-lg">
                <span class="font-medium text-gray-700">Flujo Volumétrico</span>
                <span class="text-xl font-bold text-purple-600">
                    ${results.volumetric_flow.toFixed(1)} m³/s
                </span>
            </div>
            <div class="flex justify-between items-center p-3 bg-white/50 rounded-lg">
                <span class="font-medium text-gray-700">Reynolds</span>
                <span class="text-xl font-bold text-indigo-600">
                    ${results.reynolds_number.toExponential(2)}
                </span>
            </div>
        </div>
    `;
}

function displayDetailedResults(results) {
    const table = document.getElementById('detailedResultsTable');

    const rows = [
        ['Poder Calorífico Superior', `${results.pcs.toFixed(0)} kJ/kg`],
        ['Poder Calorífico Inferior', `${results.pci_calculated.toFixed(0)} kJ/kg`],
        ['Temperatura Adiabática', `${(results.adiabatic_flame_temp - 273.15).toFixed(0)}°C`],
        ['Aire Teórico Requerido', `${results.theoretical_air.toFixed(2)} kg/kg`],
        ['Aire Real con Exceso', `${results.real_air.toFixed(2)} kg/kg`],
        ['Flujo Másico Gases', `${(results.mass_flow_gases * 3600).toFixed(0)} kg/h`],
        ['Densidad de Gases', `${results.gas_density.toFixed(3)} kg/m³`],
        ['Factor de Fricción', `${results.friction_factor.toFixed(4)}`],
        ['Coeficiente U', `${results.heat_transfer_coefficient.toFixed(2)} W/(m²·K)`],
        ['Pérdida de Calor por Metro', `${(results.heat_loss_per_meter / 1000).toFixed(2)} kW/m`],
        ['Temp. Pared Externa', `${results.external_wall_temp.toFixed(1)}°C`],
        ['Factor Emisión CO₂', `${results.co2_emission_factor.toFixed(3)} kg CO₂/kg`]
    ];

    let tableHTML = `
        <thead class="bg-gray-50">
            <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Parámetro
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Valor
                </th>
            </tr>
        </thead>
        <tbody class="bg-white/50 divide-y divide-gray-200">
    `;

    rows.forEach(([param, value]) => {
        tableHTML += `
            <tr class="hover:bg-dml-green-50/50 transition-colors">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    ${param}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                    ${value}
                </td>
            </tr>
        `;
    });

    tableHTML += '</tbody>';
    table.innerHTML = tableHTML;
}

function hideResults() {
    document.getElementById('resultsSection').classList.add('hidden');
}

function showNotification(message, type = 'info') {
    // Crear elemento de notificación
    const notification = document.createElement('div');
    notification.className = `fixed top-20 right-4 p-4 rounded-lg shadow-lg z-50
                             alert alert-${type} fade-in max-w-sm`;
    notification.innerHTML = `
        <div class="flex">
            <div class="flex-shrink-0">
                <i class="fas ${getNotificationIcon(type)}"></i>
            </div>
            <div class="ml-3">
                <p class="text-sm">${message}</p>
            </div>
            <button onclick="this.parentElement.parentElement.remove()"
                    class="ml-auto text-gray-400 hover:text-gray-600">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;

    document.body.appendChild(notification);

    // Auto-eliminar después de 5 segundos
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

function getNotificationIcon(type) {
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    return icons[type] || icons.info;
}

// Funciones de exportación (placeholder)
async function exportPDF() {
    if (!appState.currentData || !appState.results) {
        showNotification('Realice cálculos antes de exportar', 'warning');
        return;
    }

    try {
        const response = await fetch(`${appState.apiBase}/export/pdf`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(appState.currentData)
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `combustion_report_${appState.currentData.project_code}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            showNotification('PDF exportado exitosamente', 'success');
        }
    } catch (error) {
        showNotification('Error exportando PDF', 'error');
    }
}

async function exportExcel() {
    if (!appState.currentData || !appState.results) {
        showNotification('Realice cálculos antes de exportar', 'warning');
        return;
    }

    try {
        const response = await fetch(`${appState.apiBase}/export/excel`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(appState.currentData)
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `combustion_results_${appState.currentData.project_code}.xlsx`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            showNotification('Excel exportado exitosamente', 'success');
        }
    } catch (error) {
        showNotification('Error exportando Excel', 'error');
    }
}