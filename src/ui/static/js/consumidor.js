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