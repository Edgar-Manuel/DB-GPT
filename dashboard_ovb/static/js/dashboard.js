// Configuración de Sortable para cada fila
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar Sortable para cada fila
    const sortableRows = document.querySelectorAll('.sortable-row');
    sortableRows.forEach(row => {
        new Sortable(row, {
            animation: 150,
            handle: '.drag-handle',
            ghostClass: 'sortable-ghost',
            chosenClass: 'sortable-chosen',
            dragClass: 'sortable-drag',
            onEnd: function(evt) {
                saveLayout();
            }
        });
    });

    // También hacer las filas ordenables entre sí
    new Sortable(document.getElementById('dashboard-container'), {
        animation: 150,
        handle: '.drag-handle',
        ghostClass: 'sortable-ghost',
        chosenClass: 'sortable-chosen',
        dragClass: 'sortable-drag',
        draggable: '.sortable-row',
        onEnd: function(evt) {
            saveLayout();
        }
    });

    // Cargar el layout guardado
    loadLayout();
});

// Función para guardar el layout actual
function saveLayout() {
    const layout = {
        rows: []
    };

    document.querySelectorAll('.sortable-row').forEach(row => {
        const rowItems = [];
        row.querySelectorAll('.sortable-item').forEach(item => {
            rowItems.push(item.innerHTML);
        });
        layout.rows.push({
            id: row.id,
            items: rowItems
        });
    });

    localStorage.setItem('dashboardLayout', JSON.stringify(layout));
}

// Función para cargar el layout guardado
function loadLayout() {
    const savedLayout = localStorage.getItem('dashboardLayout');
    if (savedLayout) {
        const layout = JSON.parse(savedLayout);
        layout.rows.forEach(rowData => {
            const row = document.getElementById(rowData.id);
            if (row) {
                const items = row.querySelectorAll('.sortable-item');
                items.forEach((item, index) => {
                    if (rowData.items[index]) {
                        item.innerHTML = rowData.items[index];
                    }
                });
            }
        });
        
        // Reinicializar los gráficos después de cargar el layout
        if (typeof initializeCharts === 'function') {
            initializeCharts();
        }
    }
} 