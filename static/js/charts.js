// Función para cargar los datos y crear las gráficas
async function loadCharts() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        // Crear gráfico de puntuaciones
        const puntuacionesCtx = document.getElementById('puntuacionesChart').getContext('2d');
        new Chart(puntuacionesCtx, {
            type: 'bar',
            data: {
                labels: Object.keys(data.puntuaciones),
                datasets: [{
                    label: 'Número de Clientes',
                    data: Object.values(data.puntuaciones),
                    backgroundColor: '#3498db',
                    borderColor: '#2980b9',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Número de Clientes'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Puntuación'
                        }
                    }
                }
            }
        });

        // Crear gráfico de intereses
        const interesesCtx = document.getElementById('interesesChart').getContext('2d');
        const interesesData = Object.entries(data.intereses)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 10);

        new Chart(interesesCtx, {
            type: 'doughnut',
            data: {
                labels: interesesData.map(item => item[0]),
                datasets: [{
                    data: interesesData.map(item => item[1]),
                    backgroundColor: [
                        '#3498db',
                        '#2ecc71',
                        '#e74c3c',
                        '#f1c40f',
                        '#9b59b6',
                        '#1abc9c',
                        '#e67e22',
                        '#34495e',
                        '#16a085',
                        '#c0392b'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'right'
                    },
                    title: {
                        display: true,
                        text: 'Top 10 Intereses'
                    }
                }
            }
        });

    } catch (error) {
        console.error('Error al cargar los datos:', error);
    }
}

// Cargar las gráficas cuando el documento esté listo
document.addEventListener('DOMContentLoaded', loadCharts); 