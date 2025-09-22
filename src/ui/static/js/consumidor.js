window.addEventListener("DOMContentLoaded", () => {
  const messages = document.getElementById("mensajes");

  if (typeof (EventSource) !== "undefined") {
    console.log('🔌 Intentando conectar a SSE...');
    var source = new EventSource("/stream");

    source.onopen = function(event) {
      console.log('✅ SSE conectado exitosamente');
      actualizarEstadoSSE('conectado');
    };

    source.onmessage = function (event) {
      console.log('📨 SSE recibió mensaje:', event.data);

      // Ignorar mensajes de keep-alive
      if (event.data === 'ping') {
        console.log('🔄 Mensaje keep-alive recibido');
        return;
      }

      try {
        // Remover el prefijo "data: " del protocolo SSE antes de parsear JSON
        const data = event.data.replace(/^data: /, '');
        console.log('📋 Datos limpios:', data);

        const evento = JSON.parse(data);
        console.log('📋 Evento parseado:', evento);
        mostrarEvento(evento);
      } catch (e) {
        console.error('❌ Error parsing SSE data:', e, 'Raw data:', event.data);
      }
    };

    source.onerror = function(event) {
      console.error('❌ Error en SSE:', event);
      actualizarEstadoSSE('error');
    };
  } else {
    console.error('❌ EventSource no soportado por este navegador');
  }
});

function mostrarEvento(evento) {
    console.log('🎉 Mostrando evento en UI:', evento);

    // Extraer datos del nuevo formato
    const tipoEvento = evento.data?.tipoEvento || evento.tipoEvento || 'Evento';
    const idEvento = evento.data?.id_evento || evento.id_evento || evento.idEvento || 'N/A';
    const idReferido = evento.data?.idReferido || evento.idReferido || 'N/A';
    const idSocio = evento.data?.idSocio || evento.idSocio || 'N/A';
    const monto = evento.data?.monto || evento.monto || 0;
    const fechaEvento = evento.data?.fechaEvento || evento.fechaEvento || new Date().toISOString();
    const comando = evento.comando || 'N/A';

    const container = document.getElementById("eventos-tiempo-real");
    const eventoDiv = document.createElement("div");
    eventoDiv.className = "alert alert-info";
    eventoDiv.innerHTML = `
        <strong>${tipoEvento}</strong><br>
        Comando: ${comando}<br>
        ID Evento: ${idEvento}<br>
        Referido: ${idReferido}<br>
        Socio: ${idSocio}<br>
        Monto: $${monto}<br>
        Fecha: ${new Date(fechaEvento).toLocaleString()}
    `;
    container.appendChild(eventoDiv);

    // Agregar indicador visual de que funcionó
    eventoDiv.style.border = "2px solid green";
    setTimeout(() => {
        eventoDiv.style.border = "";
    }, 3000);
}

// Agregar indicador de estado SSE
function actualizarEstadoSSE(estado) {
    let statusDiv = document.getElementById("sse-status");
    if (!statusDiv) {
        statusDiv = document.createElement("div");
        statusDiv.id = "sse-status";
        statusDiv.style.position = "fixed";
        statusDiv.style.top = "10px";
        statusDiv.style.right = "10px";
        statusDiv.style.padding = "5px 10px";
        statusDiv.style.borderRadius = "5px";
        statusDiv.style.fontSize = "12px";
        document.body.appendChild(statusDiv);
    }

    if (estado === "conectado") {
        statusDiv.style.backgroundColor = "green";
        statusDiv.style.color = "white";
        statusDiv.textContent = "SSE: Conectado";
    } else if (estado === "error") {
        statusDiv.style.backgroundColor = "red";
        statusDiv.style.color = "white";
        statusDiv.textContent = "SSE: Error";
    } else {
        statusDiv.style.backgroundColor = "orange";
        statusDiv.style.color = "white";
        statusDiv.textContent = "SSE: " + estado;
    }
}

async function crearEvento(datos) {
    const query = `
    mutation CrearEvento($tipoEvento: String!, $idReferido: String!, $idSocio: String!, $monto: Float!, $estadoEvento: String!) {
        crearEvento(
            tipoEvento: $tipoEvento,
            idReferido: $idReferido,
            idSocio: $idSocio,
            monto: $monto,
            estadoEvento: $estadoEvento
        ) {
            mensaje
            codigo
        }
    }
`;

    // console.log('Query GraphQL:', query);
    // console.log('Variables GraphQL:', datos);

    const response = await fetch('/v1/graphql', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            query: query,
            variables: datos
        })
    });

    const result = await response.json();
    // console.log('Respuesta del servidor:', result);
    return result;
}

document.getElementById('eventoForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const datos = Object.fromEntries(formData);

    // console.log('Datos del formulario antes de conversión:', datos);

    // Convertir tipos de datos primero
    if (datos.monto) {
        datos.monto = parseFloat(datos.monto);
    }

    // Convertir campos con underscore a camelCase para GraphQL
    if (datos.estado_evento) {
        datos.estadoEvento = datos.estado_evento;
        delete datos.estado_evento;
    }
    if (datos.tipo_evento) {
        datos.tipoEvento = datos.tipo_evento;
        delete datos.tipo_evento;
    }

    // console.log('Datos del formulario después de conversión:', datos);

    try {
        const result = await crearEvento(datos);
        // console.log('Resultado GraphQL:', result);
        e.target.reset();
        alert('Evento creado exitosamente!');
    } catch (error) {
        console.error('Error creando evento:', error);
        alert('Error creando evento');
    }
});

// ===============================================
// NUEVA FUNCIONALIDAD: CONSULTAR EVENTOS POR SOCIO
// ===============================================

// Función para consultar eventos por socio usando GraphQL
async function consultarEventosSocio(idSocio) {
    const query = `
    query ObtenerEventosSocio($idSocio: String!) {
        eventosSocio(idSocio: $idSocio) {
            idSocio
            eventos {
                idEvento
                idReferido
                idSocio
                monto
                fechaEvento
                estadoEvento
                ganancia
                tipoEvento
            }
        }
    }
    `;

    console.log('🔍 Consultando eventos para socio:', idSocio);
    console.log('📋 Query GraphQL:', query);

    const response = await fetch('/v1/graphql', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            query: query,
            variables: { idSocio: idSocio }
        })
    });

    const result = await response.json();
    console.log('📨 Respuesta del servidor:', result);
    return result;
}

// Función para mostrar eventos del socio en la UI
function mostrarEventosSocio(eventosData) {
    const container = document.getElementById("eventos-socio");
    container.innerHTML = ""; // Limpiar contenido anterior
    
    console.log('🎨 Mostrando eventos en UI:', eventosData);
    
    // Verificar si hay errores en la respuesta GraphQL
    if (eventosData.errors) {
        container.innerHTML = `<div class="alert alert-danger">Error: ${eventosData.errors[0].message}</div>`;
        return;
    }
    
    // Verificar si hay datos
    if (eventosData.data?.eventosSocio?.eventos?.length > 0) {
        const eventos = eventosData.data.eventosSocio.eventos;
        const idSocio = eventosData.data.eventosSocio.idSocio;
        
        // Agregar header con información del socio
        const headerDiv = document.createElement("div");
        headerDiv.className = "alert alert-success mb-3";
        headerDiv.innerHTML = `
            <strong>📊 Eventos del Socio: ${idSocio}</strong><br>
            <small>Total de eventos encontrados: ${eventos.length}</small>
        `;
        container.appendChild(headerDiv);
        
        // Mostrar cada evento
        eventos.forEach((evento, index) => {
            const eventoDiv = document.createElement("div");
            eventoDiv.className = "card mb-2";
            eventoDiv.innerHTML = `
                <div class="card-body">
                    <h6 class="card-title">
                        <span class="badge bg-primary me-2">#${index + 1}</span>
                        ${evento.tipoEvento || 'Evento'}
                    </h6>
                    <div class="row">
                        <div class="col-md-6">
                            <small class="text-muted">ID Evento:</small><br>
                            <code>${evento.idEvento}</code><br><br>
                            <small class="text-muted">ID Referido:</small><br>
                            <span>${evento.idReferido}</span><br><br>
                            <small class="text-muted">Monto:</small><br>
                            <span class="fw-bold text-success">$${evento.monto?.toLocaleString() || '0'}</span>
                        </div>
                        <div class="col-md-6">
                            <small class="text-muted">Ganancia:</small><br>
                            <span class="fw-bold text-info">$${evento.ganancia?.toLocaleString() || '0'}</span><br><br>
                            <small class="text-muted">Fecha:</small><br>
                            <span>${new Date(evento.fechaEvento).toLocaleString()}</span>
                        </div>
                    </div>
                </div>
            `;
            container.appendChild(eventoDiv);
        });
    } else {
        container.innerHTML = `
            <div class="alert alert-warning">
                <strong>⚠️ No se encontraron eventos</strong><br>
                No hay eventos registrados para este socio.
            </div>
        `;
    }
}

// Función auxiliar para obtener la clase CSS según el estado
function obtenerClaseEstado(estado) {
    switch(estado?.toLowerCase()) {
        case 'pago_completado':
        case 'completado':
            return 'bg-success';
        case 'pendiente':
            return 'bg-warning';
        case 'rechazado':
        case 'fallido':
            return 'bg-danger';
        default:
            return 'bg-secondary';
    }
}

// Event listener para el formulario de consulta de eventos
document.getElementById('consultarEventosForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const idSocio = formData.get('socioId').trim();

    if (!idSocio) {
        alert('Por favor ingrese un ID de socio válido');
        return;
    }

    // Mostrar indicador de carga
    const container = document.getElementById("eventos-socio");
    container.innerHTML = `
        <div class="alert alert-info">
            <div class="d-flex align-items-center">
                <div class="spinner-border spinner-border-sm me-2" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
                Buscando eventos para el socio: ${idSocio}...
            </div>
        </div>
    `;

    try {
        console.log('🔍 Iniciando búsqueda de eventos para socio:', idSocio);
        const result = await consultarEventosSocio(idSocio);
        mostrarEventosSocio(result);
        console.log('✅ Búsqueda completada exitosamente');
    } catch (error) {
        console.error('❌ Error consultando eventos:', error);
        container.innerHTML = `
            <div class="alert alert-danger">
                <strong>❌ Error de conexión</strong><br>
                No se pudieron obtener los eventos. Verifique que el servicio esté funcionando.
            </div>
        `;
    }
});

// ============================================
// FUNCIONES PARA REFERIDOS
// ============================================
// FUNCIONES PARA EVENTOS POR SOCIO
// ============================================

// Función para mostrar/ocultar la sección de eventos por socio
function mostrarSeccionEventos() {
    const seccionEventos = document.getElementById('eventos-section');
    const seccionReferidos = document.getElementById('referidos-section');
    const seccionPagos = document.getElementById('pagos-section');
    const isVisible = seccionEventos.style.display !== 'none';
    
    if (isVisible) {
        seccionEventos.style.display = 'none';
    } else {
        seccionEventos.style.display = 'block';
        seccionReferidos.style.display = 'none';
        seccionPagos.style.display = 'none';
        // Hacer scroll suave hacia la sección
        seccionEventos.scrollIntoView({ behavior: 'smooth' });
    }
}

// ============================================
// FUNCIONES PARA REFERIDOS
// ============================================

// Función para mostrar/ocultar la sección de referidos
function mostrarSeccionReferidos() {
    const seccionEventos = document.getElementById('eventos-section');
    const seccionReferidos = document.getElementById('referidos-section');
    const seccionPagos = document.getElementById('pagos-section');
    const isVisible = seccionReferidos.style.display !== 'none';
    
    if (isVisible) {
        seccionReferidos.style.display = 'none';
    } else {
        seccionReferidos.style.display = 'block';
        seccionEventos.style.display = 'none';
        seccionPagos.style.display = 'none';
        // Hacer scroll suave hacia la sección
        seccionReferidos.scrollIntoView({ behavior: 'smooth' });
    }
}

// ============================================
// FUNCIONES PARA PAGOS
// ============================================

// Función para mostrar/ocultar la sección de pagos
function mostrarSeccionPagos() {
    const seccionEventos = document.getElementById('eventos-section');
    const seccionReferidos = document.getElementById('referidos-section');
    const seccionPagos = document.getElementById('pagos-section');
    const isVisible = seccionPagos.style.display !== 'none';
    
    if (isVisible) {
        seccionPagos.style.display = 'none';
    } else {
        seccionPagos.style.display = 'block';
        seccionEventos.style.display = 'none';
        seccionReferidos.style.display = 'none';
        // Hacer scroll suave hacia la sección
        seccionPagos.scrollIntoView({ behavior: 'smooth' });
    }
}

// Función para consultar pago por ID
async function consultarPagoInfo(idPago) {
    const query = `
    query ObtenerPagoInfo($idPago: String!) {
        pagoInfo(idPago: $idPago) {
            idTransaction
            idPago
            idSocio
            pago
            estadoPago
            fechaPago
        }
    }
    `;

    const variables = {
        idPago: idPago
    };

    console.log('🔍 Consultando pago con ID:', idPago);
    console.log('📋 Query GraphQL:', query);
    console.log('📋 Variables:', variables);

    try {
        const response = await fetch('/v1/graphql', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                variables: variables
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        console.log('📋 Respuesta GraphQL pago:', result);

        if (result.errors) {
            throw new Error('GraphQL errors: ' + JSON.stringify(result.errors));
        }

        return result;
    } catch (error) {
        console.error('❌ Error consultando pago:', error);
        throw error;
    }
}

// Función para mostrar la información del pago en la UI
function mostrarPagoInfo(pagoData) {
    const container = document.getElementById('info-pago');
    
    if (!pagoData || !pagoData.data || !pagoData.data.pagoInfo) {
        container.innerHTML = `
            <div class="alert alert-warning">
                <strong>⚠️ No se encontró información del pago</strong><br>
                No se pudo obtener la información para este ID de pago.
            </div>
        `;
        return;
    }

    const pago = pagoData.data.pagoInfo;
    
    const fechaFormateada = new Date(pago.fechaPago).toLocaleString('es-ES', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });

    let html = `
        <div class="alert alert-success">
            <strong>✅ Información del pago encontrada</strong><br>
            ID del Pago: <code>${pago.idPago}</code>
        </div>
        
        <div class="card">
            <div class="card-header bg-success text-white">
                <h5 class="mb-0">
                    <strong>💳 Información del Pago</strong>
                    <span class="badge ${obtenerClaseEstadoPago(pago.estadoPago)}">${pago.estadoPago}</span>
                </h5>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6">
                        <strong>ID Transacción:</strong> <code>${pago.idTransaction}</code><br>
                        <strong>ID Pago:</strong> <code>${pago.idPago}</code><br>
                        <strong>ID Socio:</strong> <code>${pago.idSocio}</code><br>
                    </div>
                    <div class="col-md-6">
                        <strong>Monto:</strong> <span class="text-success fw-bold">$${pago.pago.toLocaleString()}</span><br>
                        <strong>Fecha:</strong> ${fechaFormateada}<br>
                        <strong>Estado:</strong> 
                        <span class="badge ${obtenerClaseEstadoPago(pago.estadoPago)}">${pago.estadoPago}</span><br>
                    </div>
                </div>
            </div>
        </div>
    `;

    container.innerHTML = html;
}

// Función para obtener la clase CSS según el estado del pago
function obtenerClaseEstadoPago(estado) {
    switch (estado?.toUpperCase()) {
        case 'COMPLETADO':
        case 'APROBADO':
            return 'bg-success';
        case 'SOLICITADO':
        case 'PENDIENTE':
            return 'bg-warning text-dark';
        case 'RECHAZADO':
        case 'CANCELADO':
            return 'bg-danger';
        case 'ERROR':
            return 'bg-danger';
        default:
            return 'bg-secondary';
    }
}

// Event listener para el formulario de consultar pagos
document.getElementById('consultarPagosForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const idPago = document.getElementById('pagoId').value.trim();
    const container = document.getElementById('info-pago');
    
    if (!idPago) {
        container.innerHTML = `
            <div class="alert alert-warning">
                <strong>⚠️ Campo requerido</strong><br>
                Por favor ingrese el ID del pago.
            </div>
        `;
        return;
    }

    // Mostrar indicador de carga
    container.innerHTML = `
        <div class="alert alert-info">
            <div class="d-flex align-items-center">
                <div class="spinner-border spinner-border-sm me-2" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
                Buscando información del pago: ${idPago}...
            </div>
        </div>
    `;

    try {
        console.log('🔍 Iniciando búsqueda de pago con ID:', idPago);
        const result = await consultarPagoInfo(idPago);
        mostrarPagoInfo(result);
        console.log('✅ Búsqueda de pago completada exitosamente');
    } catch (error) {
        console.error('❌ Error consultando pago:', error);
        container.innerHTML = `
            <div class="alert alert-danger">
                <strong>❌ Error de conexión</strong><br>
                No se pudo obtener la información del pago. Verifique que el servicio esté funcionando.
            </div>
        `;
    }
});

// ============================================
// FUNCIONES PARA REFERIDOS
// ============================================

// Función para consultar referidos por socio
async function consultarReferidosSocio(idSocio) {
    const query = `
    query ObtenerReferidosSocio($idSocio: String!) {
        referidosSocio(idSocio: $idSocio) {
            idSocio
            referidos {
                idEvento
                idReferido
                tipoEvento
                monto
                estadoEvento
                fechaEvento
            }
        }
    }
    `;

    const variables = {
        idSocio: idSocio
    };

    console.log('🔍 Consultando referidos para socio:', idSocio);
    console.log('📋 Query GraphQL:', query);
    console.log('📋 Variables:', variables);

    try {
        const response = await fetch('/v1/graphql', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                variables: variables
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        console.log('📋 Respuesta GraphQL referidos:', result);

        if (result.errors) {
            throw new Error('GraphQL errors: ' + JSON.stringify(result.errors));
        }

        return result;
    } catch (error) {
        console.error('❌ Error consultando referidos:', error);
        throw error;
    }
}

// Función para mostrar los referidos en la UI
function mostrarReferidosSocio(referidosData) {
    const container = document.getElementById('referidos-socio');
    
    if (!referidosData || !referidosData.data || !referidosData.data.referidosSocio || !referidosData.data.referidosSocio.referidos || referidosData.data.referidosSocio.referidos.length === 0) {
        container.innerHTML = `
            <div class="alert alert-warning">
                <strong>⚠️ No se encontraron referidos</strong><br>
                No hay referidos registrados para este socio.
            </div>
        `;
        return;
    }

    const referidos = referidosData.data.referidosSocio.referidos;
    const idSocio = referidosData.data.referidosSocio.idSocio;
    
    let html = `
        <div class="alert alert-success">
            <strong>✅ Referidos encontrados</strong><br>
            Se encontraron ${referidos.length} referido(s) para el socio: <code>${idSocio}</code>
        </div>
    `;

    // Generar cards para cada referido
    referidos.forEach((referido, index) => {
        const fechaFormateada = new Date(referido.fechaEvento).toLocaleString('es-ES', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });

        html += `
            <div class="card mb-3">
                <div class="card-header bg-warning text-dark">
                    <h6 class="mb-0">
                        <strong>Referido #${index + 1}</strong>
                        <span class="badge ${obtenerClaseEstadoReferido(referido.estadoEvento)}">${referido.estadoEvento}</span>
                    </h6>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <strong>ID Evento:</strong> <code>${referido.idEvento}</code><br>
                            <strong>ID Referido:</strong> <code>${referido.idReferido}</code><br>
                            <strong>Tipo de Evento:</strong> ${referido.tipoEvento}<br>
                        </div>
                        <div class="col-md-6">
                            <strong>Monto:</strong> <span class="text-success fw-bold">$${referido.monto.toLocaleString()}</span><br>
                            <strong>Fecha:</strong> ${fechaFormateada}<br>
                            <strong>Estado:</strong> 
                            <span class="badge ${obtenerClaseEstadoReferido(referido.estadoEvento)}">${referido.estadoEvento}</span><br>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}

// Función para obtener la clase CSS según el estado del referido
function obtenerClaseEstadoReferido(estado) {
    switch (estado?.toUpperCase()) {
        case 'CONFIRMADO':
            return 'bg-success';
        case 'PENDIENTE':
            return 'bg-warning text-dark';
        case 'CANCELADO':
            return 'bg-danger';
        case 'RECHAZADO':
            return 'bg-danger';
        default:
            return 'bg-secondary';
    }
}

// Event listener para el formulario de consultar referidos
document.getElementById('consultarReferidosForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const idSocio = document.getElementById('socioIdReferidos').value.trim();
    const container = document.getElementById('referidos-socio');
    
    if (!idSocio) {
        container.innerHTML = `
            <div class="alert alert-warning">
                <strong>⚠️ Campo requerido</strong><br>
                Por favor ingrese el ID del socio.
            </div>
        `;
        return;
    }

    // Mostrar indicador de carga
    container.innerHTML = `
        <div class="alert alert-info">
            <div class="d-flex align-items-center">
                <div class="spinner-border spinner-border-sm me-2" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
                Buscando referidos para el socio: ${idSocio}...
            </div>
        </div>
    `;

    try {
        console.log('🔍 Iniciando búsqueda de referidos para socio:', idSocio);
        const result = await consultarReferidosSocio(idSocio);
        mostrarReferidosSocio(result);
        console.log('✅ Búsqueda de referidos completada exitosamente');
    } catch (error) {
        console.error('❌ Error consultando referidos:', error);
        container.innerHTML = `
            <div class="alert alert-danger">
                <strong>❌ Error de conexión</strong><br>
                No se pudieron obtener los referidos. Verifique que el servicio esté funcionando.
            </div>
        `;
    }
});