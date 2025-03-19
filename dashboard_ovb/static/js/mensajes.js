document.addEventListener('DOMContentLoaded', function() {
    // Cargar mensajes cuando se abre un modal
    const modales = document.querySelectorAll('.modal');
    modales.forEach(modal => {
        modal.addEventListener('show.bs.modal', function(event) {
            const clienteId = this.id.replace('mensajeModal', '');
            cargarMensajes(clienteId);
        });
    });

    // Manejar generación de nuevos mensajes
    const botonesGenerar = document.querySelectorAll('.generar-mensaje');
    botonesGenerar.forEach(boton => {
        boton.addEventListener('click', function() {
            const clienteId = this.dataset.clienteId;
            generarNuevoMensaje(clienteId);
        });
    });
});

function cargarMensajes(clienteId) {
    const container = document.getElementById(`mensajes-container-${clienteId}`);
    
    // Aquí se haría la petición al servidor para obtener los mensajes
    fetch(`/mensajes/${clienteId}`)
        .then(response => response.json())
        .then(mensajes => {
            container.innerHTML = '';
            mensajes.forEach(mensaje => {
                container.appendChild(crearMensajeElement(mensaje));
            });
        });
}

function generarNuevoMensaje(clienteId) {
    const boton = document.querySelector(`[data-cliente-id="${clienteId}"]`);
    boton.disabled = true;
    boton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generando...';

    // Aquí se haría la petición al servidor para generar un nuevo mensaje
    fetch(`/generar-mensaje/${clienteId}`, { method: 'POST' })
        .then(response => response.json())
        .then(mensaje => {
            const container = document.getElementById(`mensajes-container-${clienteId}`);
            const mensajeElement = crearMensajeElement(mensaje);
            mensajeElement.classList.add('mensaje-nuevo');
            container.insertBefore(mensajeElement, container.firstChild);
        })
        .finally(() => {
            boton.disabled = false;
            boton.innerHTML = '<i class="fas fa-sync"></i> Generar nuevo mensaje';
        });
}

function crearMensajeElement(mensaje) {
    const div = document.createElement('div');
    div.className = 'mensaje-card';
    div.innerHTML = `
        <div class="mensaje-header">
            <span>Generado el: ${new Date(mensaje.fecha).toLocaleString()}</span>
            <span>Tipo: ${mensaje.tipo}</span>
        </div>
        <div class="mensaje-content">${mensaje.contenido}</div>
        <div class="mensaje-footer">
            <button class="btn btn-outline-primary btn-sm copiar-mensaje">
                <i class="fas fa-copy"></i> Copiar
            </button>
        </div>
    `;
    
    div.querySelector('.copiar-mensaje').addEventListener('click', function() {
        navigator.clipboard.writeText(mensaje.contenido);
        this.innerHTML = '<i class="fas fa-check"></i> Copiado';
        setTimeout(() => {
            this.innerHTML = '<i class="fas fa-copy"></i> Copiar';
        }, 2000);
    });

    return div;
} 