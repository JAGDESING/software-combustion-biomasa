// Análisis de sensibilidad dinámico
// Sistema de Cálculo Energético de Biomasa

let sensitivityChart = null;

// Actualizar análisis de sensibilidad
async function updateSensitivityAnalysis() {
    if (!appState.currentData) {
        console.log('No hay datos para análisis de sensibilidad');
        return;
    }

    const paramName = document.getElementById('sensitivityParam').value;

    try {
        // Mostrar indicador de carga en el gráfico
        const chartDiv = document.getElementById('sensitivityChart');
        chartDiv.innerHTML = `
            <div class="flex items-center justify-center h-full">
                <div class="text-center">
                    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-dml-green-600 mx-auto mb-4"></div>
                    <p class="text-gray-600">Realizando análisis de sensibilidad...</p>
                </div>
            </div>
        `;

        // Realizar análisis en el backend
        const response = await fetch(`${appState.apiBase}/sensitivity`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                parameter: paramName,
                range_percent: 50,
                num_points: 20,
                input_data: appState.currentData
            })
        });

        if (!response.ok) {
            throw new Error('Error en análisis de sensibilidad');
        }

        const results = await response.json();

        // Crear gráfico de sensibilidad
        createSensitivityChart(results, paramName);

        // Mostrar recomendaciones
        displaySensitivityRecommendations(results, paramName);

    } catch (error) {
        console.error('Error en análisis de sensibilidad:', error);
        document.getElementById('sensitivityChart').innerHTML = `
            <div class="flex items-center justify-center h-full">
                <div class="text-center text-red-600">
                    <i class="fas fa-exclamation-triangle text-4xl mb-4"></i>
                    <p>Error al realizar análisis de sensibilidad</p>
                </div>
            </div>
        `;
    }
}

// Crear gráfico de sensibilidad
function createSensitivityChart(data, paramName) {
    // Preparar datos para múltiples trazas
    const temperatureTrace = {
        x: data.parameter_values,
        y: data.temperatures.map(t => t - 273.15), // Convertir a °C
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Temperatura (°C)',
        yaxis: 'y',
        line: {
            color: '#ef4444',
            width: 3
        },
        marker: {
            size: 6,
            color: '#ef4444',
            line: {
                color: 'white',
                width: 2
            }
        },
        hovertemplate: `<b>${getParamLabel(paramName)}</b>: %{x:.2f}<br>` +
                      `<b>Temperatura</b>: %{y:.1f}°C<extra></extra>`
    };

    const velocityTrace = {
        x: data.parameter_values,
        y: data.velocities,
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Velocidad (m/s)',
        yaxis: 'y2',
        line: {
            color: '#3b82f6',
            width: 3
        },
        marker: {
            size: 6,
            color: '#3b82f6',
            line: {
                color: 'white',
                width: 2
            }
        },
        hovertemplate: `<b>${getParamLabel(paramName)}</b>: %{x:.2f}<br>` +
                      `<b>Velocidad</b>: %{y:.2f} m/s<extra></extra>`
    };

    const efficiencyTrace = {
        x: data.parameter_values,
        y: data.efficiencies,
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Eficiencia (%)',
        yaxis: 'y3',
        line: {
            color: '#22c55e',
            width: 3,
            dash: 'dot'
        },
        marker: {
            size: 6,
            color: '#22c55e',
            line: {
                color: 'white',
                width: 2
            }
        },
        hovertemplate: `<b>${getParamLabel(paramName)}</b>: %{x:.2f}<br>` +
                      `<b>Eficiencia</b>: %{y:.1f}%<extra></extra>`
    };

    const pressureTrace = {
        x: data.parameter_values,
        y: data.pressure_drops,
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Caída Presión (Pa/m)',
        yaxis: 'y4',
        line: {
            color: '#f59e0b',
            width: 3,
            dash: 'dash'
        },
        marker: {
            size: 6,
            color: '#f59e0b',
            line: {
                color: 'white',
                width: 2
            }
        },
        hovertemplate: `<b>${getParamLabel(paramName)}</b>: %{x:.2f}<br>` +
                      `<b>Caída Presión</b>: %{y:.1f} Pa/m<extra></extra>`
    };

    const traces = [temperatureTrace, velocityTrace, efficiencyTrace, pressureTrace];

    // Layout para múltiples ejes
    const layout = {
        title: {
            text: `Análisis de Sensibilidad: ${getParamLabel(paramName)}`,
            font: {
                size: 18,
                color: '#16a34a'
            }
        },
        xaxis: {
            title: getParamLabel(paramName),
            titlefont: {
                size: 14,
                color: '#666'
            },
            tickfont: {
                color: '#666'
            },
            gridcolor: 'rgba(0, 0, 0, 0.1)',
            zeroline: false
        },
        yaxis: {
            title: 'Temperatura (°C)',
            titlefont: {
                color: '#ef4444',
                size: 14
            },
            tickfont: {
                color: '#ef4444'
            },
            anchor: 'x',
            side: 'left',
            position: 0,
            gridcolor: 'rgba(0, 0, 0, 0.1)'
        },
        yaxis2: {
            title: 'Velocidad (m/s)',
            titlefont: {
                color: '#3b82f6',
                size: 14
            },
            tickfont: {
                color: '#3b82f6'
            },
            anchor: 'x',
            side: 'right',
            overlaying: 'y',
            position: 0.95,
            gridcolor: 'rgba(0, 0, 0, 0)'
        },
        yaxis3: {
            title: 'Eficiencia (%)',
            titlefont: {
                color: '#22c55e',
                size: 14
            },
            tickfont: {
                color: '#22c55e'
            },
            anchor: 'free',
            side: 'right',
            position: 0.97,
            gridcolor: 'rgba(0, 0, 0, 0)'
        },
        yaxis4: {
            title: 'Caída Presión (Pa/m)',
            titlefont: {
                color: '#f59e0b',
                size: 14
            },
            tickfont: {
                color: '#f59e0b'
            },
            anchor: 'free',
            side: 'left',
            position: 0.03,
            gridcolor: 'rgba(0, 0, 0, 0)'
        },
        plot_bgcolor: 'rgba(255, 255, 255, 0.5)',
        paper_bgcolor: 'rgba(255, 255, 255, 0.3)',
        margin: {
            t: 50,
            b: 60,
            l: 80,
            r: 80
        },
        hovermode: 'x unified',
        legend: {
            x: 0.5,
            y: -0.2,
            orientation: 'h',
            bgcolor: 'rgba(255, 255, 255, 0.9)',
            bordercolor: '#16a34a',
            borderwidth: 1,
            tracegroupgap: 10
        },
        shapes: [
            // Línea vertical en el valor base
            {
                type: 'line',
                x0: appState.currentData[paramName],
                y0: 0,
                x1: appState.currentData[paramName],
                y1: 1,
                yref: 'paper',
                line: {
                    color: '#16a34a',
                    width: 2,
                    dash: 'dashdot'
                },
                opacity: 0.5
            }
        ],
        annotations: [
            {
                x: appState.currentData[paramName],
                y: 1.05,
                yref: 'paper',
                text: 'Valor Base',
                showarrow: true,
                arrowhead: 2,
                arrowsize: 1,
                arrowwidth: 2,
                arrowcolor: '#16a34a',
                ax: 0,
                ay: -20
            }
        ]
    };

    const config = {
        responsive: true,
        displayModeBar: true,
        displaylogo: false,
        modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
        toImageButtonOptions: {
            format: 'png',
            filename: `sensitivity_${paramName}`,
            height: 600,
            width: 1000,
            scale: 2
        }
    };

    // Crear o actualizar el gráfico
    Plotly.newPlot('sensitivityChart', traces, layout, config);

    // Agregar eventos de hover
    document.getElementById('sensitivityChart').on('plotly_hover', function(data) {
        // Resaltar información relacionada
        updateRelatedInfo(data.points[0]);
    });

    document.getElementById('sensitivityChart').on('plotly_unhover', function(data) {
        // Restaurar información
        resetRelatedInfo();
    });
}

// Mostrar recomendaciones basadas en sensibilidad
function displaySensitivityRecommendations(results, paramName) {
    // Calcular métricas de sensibilidad
    const tempRange = Math.max(...results.temperatures) - Math.min(...results.temperatures);
    const velRange = Math.max(...results.velocities) - Math.min(...results.velocities);
    const effRange = Math.max(...results.efficiencies) - Math.min(...results.efficiencies);

    // Crear panel de recomendaciones
    const recommendationsDiv = document.getElementById('sensitivityRecommendations');

    if (!recommendationsDiv) {
        // Crear contenedor de recomendaciones si no existe
        const container = document.createElement('div');
        container.id = 'sensitivityRecommendations';
        container.className = 'mt-6 p-4 bg-dml-yellow-100/80 backdrop-blur-sm rounded-lg';
        document.getElementById('sensitivityChart').appendChild(container);
    }

    let recommendations = [];

    // Generar recomendaciones basadas en el parámetro y rangos
    switch(paramName) {
        case 'excess_air':
            if (tempRange > 200) {
                recommendations.push('⚠️ Alta sensibilidad de temperatura al aire en exceso. Considere control preciso.');
            }
            if (effRange > 10) {
                recommendations.push('📊 La eficiencia varía significativamente. Optimice el nivel de aire en exceso.');
            }
            break;

        case 'furnace_efficiency':
            if (velRange > 5) {
                recommendations.push('🌡️ La velocidad de gases es sensible a la eficiencia. Verifique el estado del horno.');
            }
            break;

        case 'moisture':
            if (tempRange > 300) {
                recommendations.push('💧 La humedad del combustible afecta fuertemente la temperatura. Considere secado.');
            }
            if (effRange > 15) {
                recommendations.push('⚡ Alta sensibilidad en eficiencia. Control de calidad del combustible es crítico.');
            }
            break;

        case 'flow_rate':
            if (velRange > 10) {
                recommendations.push('🚀 La velocidad aumenta rápidamente con el flujo. Verifique límites de diseño.');
            }
            break;
    }

    // Agregar recomendación general
    if (recommendations.length === 0) {
        recommendations.push('✅ El sistema muestra buena estabilidad para este parámetro.');
    }

    // Mostrar recomendaciones
    document.getElementById('sensitivityRecommendations').innerHTML = `
        <h4 class="font-semibold text-dml-green-800 mb-2">Recomendaciones:</h4>
        <ul class="space-y-1 text-sm">
            ${recommendations.map(rec => `<li>${rec}</li>`).join('')}
        </ul>
        <div class="mt-3 text-xs text-gray-600">
            <strong>Rangos observados:</strong>
            Temp: ±${(tempRange/2).toFixed(0)}°C |
            Vel: ±${(velRange/2).toFixed(1)}m/s |
            Eficiencia: ±${(effRange/2).toFixed(1)}%
        </div>
    `;
}

// Obtener etiqueta del parámetro
function getParamLabel(paramName) {
    const labels = {
        'excess_air': 'Aire en Exceso (%)',
        'furnace_efficiency': 'Eficiencia del Horno (%)',
        'moisture': 'Humedad del Combustible (%)',
        'flow_rate': 'Flujo de Biomasa (ton/h)',
        'carbon': 'Carbono (%)',
        'hydrogen': 'Hidrógeno (%)',
        'oxygen': 'Oxígeno (%)',
        'duct_diameter': 'Diámetro del Ducto (pulg)',
        'reported_PCI': 'Poder Calorífico (kJ/kg)'
    };

    return labels[paramName] || paramName;
}

// Actualizar información relacionada al hacer hover
function updateRelatedInfo(point) {
    // Resaltar valores actuales en otros paneles
    const value = point.x;

    // Actualizar indicadores en la vista principal
    updateMainIndicators(point, value);
}

// Resetear información relacionada
function resetRelatedInfo() {
    // Restaurar estado normal
    document.querySelectorAll('.highlighted').forEach(el => {
        el.classList.remove('highlighted');
    });
}

// Actualizar indicadores principales
function updateMainIndicators(point, value) {
    // Lógica para actualizar otros elementos visuales
    // Por ejemplo, resaltar la temperatura actual si se está viendo el gráfico de temperatura
    if (point.curveNumber === 0) { // Temperatura
        const tempDisplay = document.querySelector('[data-temp-display]');
        if (tempDisplay) {
            tempDisplay.classList.add('highlighted');
            tempDisplay.textContent = `${value.toFixed(1)}°C`;
        }
    }
}

// Función para análisis de sensibilidad múltiple
async function runMultiParameterAnalysis() {
    const params = ['excess_air', 'furnace_efficiency', 'moisture', 'flow_rate'];

    try {
        const response = await fetch(`${appState.apiBase}/multi-sensitivity`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                parameters: params,
                range_percent: 30,
                input_data: appState.currentData
            })
        });

        if (!response.ok) throw new Error('Error en análisis múltiple');

        const results = await response.json();

        // Mostrar gráfico comparativo
        createComparativeSensitivityChart(results);

        // Mostrar ranking de sensibilidad
        displaySensitivityRanking(results.sensitivity_ranking);

    } catch (error) {
        console.error('Error en análisis múltiple:', error);
    }
}

// Crear gráfico comparativo de sensibilidad
function createComparativeSensitivityChart(results) {
    const data = Object.entries(results.individual_analysis).map(([param, analysis]) => ({
        type: 'bar',
        x: [getParamLabel(param)],
        y: [analysis.metrics.maximum_sensitivity.efficiency],
        name: getParamLabel(param),
        orientation: 'v'
    }));

    const layout = {
        title: 'Comparación de Sensibilidad - Eficiencia',
        xaxis: {
            title: 'Parámetros'
        },
        yaxis: {
            title: 'Sensibilidad Máxima (%)'
        },
        plot_bgcolor: 'rgba(255, 255, 255, 0.5)',
        paper_bgcolor: 'rgba(255, 255, 255, 0.3)'
    };

    Plotly.newPlot('comparativeSensitivityChart', data, layout);
}

// Mostrar ranking de sensibilidad
function displaySensitivityRanking(ranking) {
    const container = document.getElementById('sensitivityRanking');

    if (!container) {
        const div = document.createElement('div');
        div.id = 'sensitivityRanking';
        div.className = 'mt-6 p-4 bg-dml-blue-100/80 backdrop-blur-sm rounded-lg';
        document.querySelector('#sensitivityChart').appendChild(div);
    }

    const html = `
        <h4 class="font-semibold text-dml-blue-800 mb-3">Ranking de Sensibilidad:</h4>
        <ol class="space-y-2">
            ${ranking.map((item, index) => `
                <li class="flex items-center justify-between">
                    <span class="font-medium">${index + 1}. ${getParamLabel(item.parameter)}</span>
                    <span class="badge ${item.sensitivity_index > 20 ? 'badge-red' :
                                    item.sensitivity_index > 10 ? 'badge-yellow' : 'badge-green'}">
                        ${item.sensitivity_index.toFixed(1)}%
                    </span>
                </li>
            `).join('')}
        </ol>
    `;

    document.getElementById('sensitivityRanking').innerHTML = html;
}

// Función para optimizar parámetro
async function optimizeParameter(paramName) {
    try {
        const response = await fetch(`${appState.apiBase}/optimize`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                parameter: paramName,
                objective: 'efficiency',
                input_data: appState.currentData
            })
        });

        if (!response.ok) throw new Error('Error en optimización');

        const result = await response.json();

        // Mostrar resultados de optimización
        displayOptimizationResults(result);

    } catch (error) {
        console.error('Error en optimización:', error);
    }
}

// Mostrar resultados de optimización
function displayOptimizationResults(result) {
    const improvement = ((result.optimal_value - result.original_value) / result.original_value * 100);

    showNotification(`
        Optimización completada:<br>
        Valor óptimo: ${result.optimal_value.toFixed(2)}<br>
        Mejora: ${improvement > 0 ? '+' : ''}${improvement.toFixed(1)}%
    `, improvement > 0 ? 'success' : 'warning');
}

// Exportar funciones para uso global
window.sensitivityFunctions = {
    updateSensitivityAnalysis,
    runMultiParameterAnalysis,
    optimizeParameter
};