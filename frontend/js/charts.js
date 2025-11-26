// Gráficos dinámicos con Plotly.js
// Sistema de Cálculo Energético de Biomasa

// Crear gráficos principales
function createCharts(results) {
    createTemperatureChart(results);
    createFlowChart(results);
    createEnergyBalanceChart(results);
    createGasCompositionPieChart(results);
}

// Gráfico de temperaturas
function createTemperatureChart(results) {
    const data = [{
        x: ['Ambiente', 'Temp. Adiabática', 'Salida Horno'],
        y: [
            parseFloat(document.getElementById('dryBulbTemp').value),
            results.adiabatic_flame_temp - 273.15,
            results.outlet_gas_temp - 273.15
        ],
        type: 'bar',
        marker: {
            color: [
                'rgba(59, 130, 246, 0.6)',
                'rgba(239, 68, 68, 0.6)',
                'rgba(34, 197, 94, 0.6)'
            ],
            line: {
                color: ['rgb(59, 130, 246)', 'rgb(239, 68, 68)', 'rgb(34, 197, 94)'],
                width: 2
            }
        },
        name: 'Temperatura',
        text: [
            `${parseFloat(document.getElementById('dryBulbTemp').value)}°C`,
            `${(results.adiabatic_flame_temp - 273.15).toFixed(0)}°C`,
            `${(results.outlet_gas_temp - 273.15).toFixed(0)}°C`
        ],
        textposition: 'auto'
    }];

    const layout = {
        title: {
            text: 'Perfil de Temperaturas del Sistema',
            font: {
                size: 18,
                color: '#16a34a'
            }
        },
        yaxis: {
            title: 'Temperatura (°C)',
            titlefont: {
                color: '#16a34a',
                size: 14
            },
            tickfont: {
                color: '#666'
            }
        },
        xaxis: {
            titlefont: {
                size: 14
            }
        },
        showlegend: false,
        plot_bgcolor: 'rgba(255, 255, 255, 0.5)',
        paper_bgcolor: 'rgba(255, 255, 255, 0.3)',
        margin: {
            t: 50,
            b: 60,
            l: 70,
            r: 30
        },
        hoverlabel: {
            bgcolor: 'rgba(34, 197, 94, 0.8)',
            font: {
                color: 'white'
            }
        }
    };

    const config = {
        responsive: true,
        displayModeBar: true,
        displaylogo: false,
        modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
    };

    Plotly.newPlot('temperatureChart', data, layout, config);
}

// Gráfico de flujo y caída de presión
function createFlowChart(results) {
    // Datos para gráfico de barras dobles
    const trace1 = {
        x: ['Velocidad (m/s)', 'Caída Presión (Pa/m)'],
        y: [results.gas_velocity, results.pressure_drop / 10], // Escalar caída de presión
        name: 'Valores Actuales',
        type: 'bar',
        marker: {
            color: 'rgba(34, 197, 94, 0.6)',
            line: {
                color: 'rgb(34, 197, 94)',
                width: 2
            }
        }
    };

    const trace2 = {
        x: ['Velocidad (m/s)', 'Caída Presión (Pa/m)'],
        y: [15, 30], // Valores de referencia
        name: 'Valores Referencia',
        type: 'bar',
        marker: {
            color: 'rgba(250, 204, 21, 0.6)',
            line: {
                color: 'rgb(250, 204, 21)',
                width: 2
            }
        }
    };

    const data = [trace1, trace2];

    const layout = {
        title: {
            text: 'Parámetros de Flujo',
            font: {
                size: 18,
                color: '#16a34a'
            }
        },
        yaxis: {
            title: 'Valor',
            titlefont: {
                color: '#16a34a',
                size: 14
            }
        },
        xaxis: {
            titlefont: {
                size: 14
            }
        },
        barmode: 'group',
        plot_bgcolor: 'rgba(255, 255, 255, 0.5)',
        paper_bgcolor: 'rgba(255, 255, 255, 0.3)',
        legend: {
            x: 0.05,
            y: 0.95,
            bgcolor: 'rgba(255, 255, 255, 0.8)',
            bordercolor: '#16a34a',
            borderwidth: 1
        },
        margin: {
            t: 50,
            b: 60,
            l: 70,
            r: 30
        },
        annotations: [
            {
                x: 'Velocidad (m/s)',
                y: results.gas_velocity,
                text: `${results.gas_velocity.toFixed(1)} m/s`,
                showarrow: true,
                arrowhead: 2,
                arrowsize: 1,
                arrowwidth: 2,
                arrowcolor: '#16a34a'
            }
        ]
    };

    const config = {
        responsive: true,
        displayModeBar: true,
        displaylogo: false,
        modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
    };

    Plotly.newPlot('flowChart', data, layout, config);
}

// Gráfico de balance de energía
function createEnergyBalanceChart(results) {
    const data = [{
        values: [
            results.useful_energy,
            results.chimney_losses,
            results.total_energy_released - results.useful_energy - results.chimney_losses
        ],
        labels: ['Energía Útil', 'Pérdidas Chimenea', 'Otras Pérdidas'],
        type: 'pie',
        marker: {
            colors: [
                'rgba(34, 197, 94, 0.7)',
                'rgba(239, 68, 68, 0.7)',
                'rgba(250, 204, 21, 0.7)'
            ],
            line: {
                color: 'white',
                width: 2
            }
        },
        textinfo: 'label+percent',
        textposition: 'outside',
        automargin: true,
        hovertemplate: '%{label}<br>%{value:.2f} MW<br>%{percent}<extra></extra>'
    }];

    const layout = {
        title: {
            text: 'Balance Energético del Sistema',
            font: {
                size: 18,
                color: '#16a34a'
            }
        },
        plot_bgcolor: 'rgba(255, 255, 255, 0.5)',
        paper_bgcolor: 'rgba(255, 255, 255, 0.3)',
        showlegend: true,
        legend: {
            x: 0.05,
            y: 0.5,
            bgcolor: 'rgba(255, 255, 255, 0.8)',
            bordercolor: '#16a34a',
            borderwidth: 1
        },
        margin: {
            t: 50,
            b: 20,
            l: 20,
            r: 120
        },
        annotations: [
            {
                text: `Total: ${results.total_energy_released.toFixed(2)} MW`,
                x: 0.5,
                y: -0.15,
                showarrow: false,
                font: {
                    size: 14,
                    color: '#666'
                }
            }
        ]
    };

    const config = {
        responsive: true,
        displayModeBar: true,
        displaylogo: false,
        modeBarButtonsToRemove: ['zoom2d', 'pan2d', 'lasso2d', 'select2d']
    };

    // Crear contenedor si no existe
    if (!document.getElementById('energyBalanceChart')) {
        const chartsSection = document.querySelector('#resultsSection');
        const chartContainer = document.createElement('div');
        chartContainer.className = 'bg-white/80 backdrop-blur-sm rounded-xl shadow-xl p-6 mb-8';
        chartContainer.innerHTML = `
            <h3 class="text-lg font-bold text-gray-800 mb-4">
                <i class="fas fa-balance-scale mr-2 text-purple-500"></i>Balance Energético
            </h3>
            <div id="energyBalanceChart" class="h-80"></div>
        `;
        chartsSection.insertBefore(chartContainer, chartsSection.children[1]);
    }

    Plotly.newPlot('energyBalanceChart', data, layout, config);
}

// Gráfico de composición de gases (circular)
function createGasCompositionPieChart(results) {
    const data = [{
        values: [
            results.co2_fraction_vol,
            results.h2o_fraction_vol,
            results.o2_fraction_vol,
            results.n2_fraction_vol,
            results.so2_fraction_vol
        ],
        labels: ['CO₂', 'H₂O', 'O₂', 'N₂', 'SO₂'],
        type: 'pie',
        sort: false,
        marker: {
            colors: [
                'rgba(239, 68, 68, 0.7)',
                'rgba(59, 130, 246, 0.7)',
                'rgba(250, 204, 21, 0.7)',
                'rgba(34, 197, 94, 0.7)',
                'rgba(168, 85, 247, 0.7)'
            ],
            line: {
                color: 'white',
                width: 2
            }
        },
        textinfo: 'label+percent',
        textposition: 'outside',
        automargin: true
    }];

    const layout = {
        title: {
            text: 'Composición de Gases de Combustión',
            font: {
                size: 18,
                color: '#16a34a'
            }
        },
        plot_bgcolor: 'rgba(255, 255, 255, 0.5)',
        paper_bgcolor: 'rgba(255, 255, 255, 0.3)',
        showlegend: true,
        legend: {
            orientation: 'h',
            x: 0.5,
            y: -0.1,
            xanchor: 'center'
        },
        margin: {
            t: 50,
            b: 80,
            l: 20,
            r: 20
        }
    };

    const config = {
        responsive: true,
        displayModeBar: true,
        displaylogo: false
    };

    // Crear contenedor si no existe
    if (!document.getElementById('gasCompositionPieChart')) {
        const chartsSection = document.querySelector('#resultsSection');
        const chartContainer = document.createElement('div');
        chartContainer.className = 'bg-white/80 backdrop-blur-sm rounded-xl shadow-xl p-6 mb-8';
        chartContainer.innerHTML = `
            <h3 class="text-lg font-bold text-gray-800 mb-4">
                <i class="fas fa-chart-pie mr-2 text-indigo-500"></i>Distribución de Gases
            </h3>
            <div id="gasCompositionPieChart" class="h-80"></div>
        `;
        chartsSection.insertBefore(chartContainer, chartsSection.children[2]);
    }

    Plotly.newPlot('gasCompositionPieChart', data, layout, config);
}

// Actualizar gráficos dinámicamente
function updateCharts(newResults) {
    // Actualizar gráfico de temperaturas con animación
    Plotly.animate('temperatureChart', {
        data: [{
            y: [
                parseFloat(document.getElementById('dryBulbTemp').value),
                newResults.adiabatic_flame_temp - 273.15,
                newResults.outlet_gas_temp - 273.15
            ],
            text: [
                `${parseFloat(document.getElementById('dryBulbTemp').value)}°C`,
                `${(newResults.adiabatic_flame_temp - 273.15).toFixed(0)}°C`,
                `${(newResults.outlet_gas_temp - 273.15).toFixed(0)}°C`
            ]
        }]
    }, {
        transition: {
            duration: 500,
            easing: 'cubic-in-out'
        },
        frame: {
            duration: 500
        }
    });

    // Similar para otros gráficos
    updateFlowChart(newResults);
}

function updateFlowChart(results) {
    Plotly.react('flowChart', [{
        x: ['Velocidad (m/s)', 'Caída Presión (Pa/m)'],
        y: [results.gas_velocity, results.pressure_drop / 10],
        name: 'Valores Actuales',
        type: 'bar',
        marker: {
            color: 'rgba(34, 197, 94, 0.6)',
            line: {
                color: 'rgb(34, 197, 94)',
                width: 2
            }
        }
    }, {
        x: ['Velocidad (m/s)', 'Caída Presión (Pa/m)'],
        y: [15, 30],
        name: 'Valores Referencia',
        type: 'bar',
        marker: {
            color: 'rgba(250, 204, 21, 0.6)',
            line: {
                color: 'rgb(250, 204, 21)',
                width: 2
            }
        }
    }]);
}

// Función para exportar gráficos
function exportChart(chartId, filename) {
    Plotly.downloadImage(chartId, {
        format: 'png',
        width: 1200,
        height: 800,
        filename: filename
    });
}

// Función para crear gráfico de series temporales (si se requiere en el futuro)
function createTimeSeriesChart(data) {
    const trace = {
        x: data.timestamps,
        y: data.values,
        type: 'scatter',
        mode: 'lines+markers',
        name: data.seriesName,
        line: {
            color: 'rgba(34, 197, 94, 0.8)',
            width: 3
        },
        marker: {
            size: 6,
            color: 'rgba(34, 197, 94, 1)',
            line: {
                color: 'white',
                width: 2
            }
        }
    };

    const layout = {
        title: data.title,
        xaxis: {
            title: 'Tiempo',
            type: 'date'
        },
        yaxis: {
            title: data.yAxisTitle
        },
        plot_bgcolor: 'rgba(255, 255, 255, 0.5)',
        paper_bgcolor: 'rgba(255, 255, 255, 0.3)'
    };

    Plotly.newPlot(data.containerId, [trace], layout);
}

// Función para crear gráfico 3D de superficie (si se requiere)
function createSurfaceChart(data) {
    const zData = [];
    for (let i = 0; i < data.z.length; i++) {
        zData.push(data.z[i]);
    }

    const surfaceData = [{
        z: zData,
        x: data.x,
        y: data.y,
        type: 'surface',
        colorscale: [
            [0, 'rgba(34, 197, 94, 0.2)'],
            [0.5, 'rgba(34, 197, 94, 0.6)'],
            [1, 'rgba(34, 197, 94, 1)']
        ],
        contours: {
            z: {
                show: true,
                usecolormap: true,
                highlightcolor: "#42f462",
                project: { z: true }
            }
        }
    }];

    const layout = {
        title: data.title,
        autosize: false,
        width: 800,
        height: 600,
        scene: {
            xaxis: { title: data.xAxisTitle },
            yaxis: { title: data.yAxisTitle },
            zaxis: { title: data.zAxisTitle }
        }
    };

    Plotly.newPlot(data.containerId, surfaceData, layout);
}

// Inicializar tooltips personalizados para gráficos
function initializeChartTooltips() {
    document.addEventListener('plotly_hover', function(data) {
        const point = data.points[0];
        // Personalizar tooltip si es necesario
    });

    document.addEventListener('plotly_unhover', function(data) {
        // Limpiar tooltips personalizados
    });
}

// Agregar listener para inicializar tooltips cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
    initializeChartTooltips();
});

// Exportar funciones para uso global
window.chartFunctions = {
    createCharts,
    updateCharts,
    exportChart,
    createTimeSeriesChart,
    createSurfaceChart
};