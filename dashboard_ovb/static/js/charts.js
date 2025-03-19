// Configuración común para los gráficos
const commonOptions = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
        legend: {
            position: 'bottom'
        }
    }
};

// Colores para los gráficos
const chartColors = [
    'rgba(255, 99, 132, 0.8)',
    'rgba(54, 162, 235, 0.8)',
    'rgba(255, 206, 86, 0.8)',
    'rgba(75, 192, 192, 0.8)',
    'rgba(153, 102, 255, 0.8)',
    'rgba(255, 159, 64, 0.8)'
];

// Gráfico de puntuaciones
const puntuacionesCtx = document.getElementById('puntuacionesChart');
if (puntuacionesCtx) {
    new Chart(puntuacionesCtx, {
        type: 'bar',
        data: {
            labels: ['0-20', '21-40', '41-60', '61-80', '81-100'],
            datasets: [{
                label: 'Número de Clientes',
                data: [15, 25, 35, 45, 30],
                backgroundColor: chartColors,
                borderColor: chartColors.map(color => color.replace('0.8', '1')),
                borderWidth: 1
            }]
        },
        options: {
            ...commonOptions,
            aspectRatio: 2,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 10
                    },
                    grid: {
                        drawBorder: false
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// Gráfico de intereses
const interesesCtx = document.getElementById('interesesChart');
if (interesesCtx) {
    new Chart(interesesCtx, {
        type: 'doughnut',
        data: {
            labels: ['Inversión', 'Seguros', 'Pensiones', 'Ahorro', 'Otros'],
            datasets: [{
                data: [30, 25, 20, 15, 10],
                backgroundColor: chartColors,
                borderColor: chartColors.map(color => color.replace('0.8', '1')),
                borderWidth: 1
            }]
        },
        options: {
            ...commonOptions,
            aspectRatio: 2,
            cutout: '60%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20
                    }
                }
            }
        }
    });
}

// Función para actualizar los gráficos con datos dinámicos
function actualizarGraficos(datos) {
    if (!datos) return;

    const puntuacionesChart = Chart.getChart('puntuacionesChart');
    if (puntuacionesChart) {
        puntuacionesChart.data.datasets[0].data = datos.puntuaciones;
        puntuacionesChart.update();
    }

    const interesesChart = Chart.getChart('interesesChart');
    if (interesesChart) {
        interesesChart.data.datasets[0].data = datos.intereses;
        interesesChart.update();
    }
} 