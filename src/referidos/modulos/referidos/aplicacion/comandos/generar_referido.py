# Comando: GenerarReferidoCommand
# Propósito: Generar un referido basado en un evento registrado

from modulos.referidos.aplicacion.comandos.base import CrearReferidoBaseHandler
from modulos.referidos.infraestructura.mapeadores import MapeadorReferido
from modulos.referidos.aplicacion.dto import ReferidoDTO
from modulos.referidos.dominio.entidades import Referido
from modulos.referidos.infraestructura.despachadores import Despachador
from seedwork.infraestructura.uow import UnidadTrabajoPuerto
from seedwork.aplicacion.comandos import Comando
from dataclasses import dataclass, field
from seedwork.aplicacion.comandos import ejecutar_commando as comando
from modulos.referidos.infraestructura.repositorios import RepositorioReferidos
from modulos.referidos.dominio.objetos_valor import EstadoReferido, TipoEvento

import datetime

@dataclass
class GenerarReferidoCommand(Comando):
    """
    Comando para generar un referido basado en un EventoRegistrado
    Estructura según especificación:
    {   
        "idEvento": "uuid",
        "tipoEvento": "venta_creada",
        "idReferido": "123e4567-e89b-12d3-a456-426614174004",
        "monto": 150.50,
        "estado": "pendiente",
        "fechaEvento": "2025-09-09T20:00:00Z"
    }
    """
    idEvento: str
    tipoEvento: str
    idReferido: str
    idSocio: str  # Derivado del evento o contexto
    monto: float
    fechaEvento: str
    estado: str = "pendiente"  # Por defecto pendiente

class GenerarReferidoHandler(CrearReferidoBaseHandler):
    """
    Handler para procesar el comando GenerarReferidoCommand
    """
    def handle(self, comando: GenerarReferidoCommand):
        # Crear DTO del referido
        referido_dto = ReferidoDTO(
            idSocio=comando.idSocio,
            idReferido=comando.idReferido,
            monto=comando.monto,
            estado=comando.estado,
            fechaEvento=comando.fechaEvento,
            tipoEvento=comando.tipoEvento,
            idEvento=comando.idEvento,
            fecha_creacion="",  # Se asignará en el dominio
            fecha_actualizacion=""  # Se asignará en el dominio
        )
        
        # Crear entidad de dominio
        referido: Referido = self.fabrica_referidos.crear_objeto(referido_dto, MapeadorReferido())
        
        print("======================")
        print(f"GenerarReferidoHandler - Procesando evento: {comando.tipoEvento}")
        print(f"IdEvento: {comando.idEvento}, IdSocio: {comando.idSocio}, IdReferido: {comando.idReferido}")
        print("======================")
        
        # Crear el referido en el dominio
        referido.crear_referido(referido)

        # Persistir en repositorio
        repositorio = self.fabrica_repositorio.crear_objeto(RepositorioReferidos.__class__)

        print("======================")
        print("Referido generado exitosamente, persistiendo en BD usando UoW...")
        print("======================")

        # Usar Unit of Work para persistencia
        from seedwork.infraestructura.uow import unidad_de_trabajo
        
        try:
            # Obtener UoW y repositorio
            uow = unidad_de_trabajo()
            repositorio = self.fabrica_repositorio.crear_objeto(RepositorioReferidos.__class__)
            
            print(f"🔄 [UoW] Iniciando transacción para referido: {referido.id}")
            
            with uow:
                # Registrar operación de agregar en UoW
                uow.registrar_batch(repositorio.agregar, referido)
                print(f"� [UoW] Batch registrado - Total batches: {len(uow.batches)}")
                
                # Commit de la UoW (ejecutará todos los batches)
                uow.commit()
                print("✅ [UoW] Referido persistido exitosamente usando UoW!")
                
        except Exception as e:
            print(f"❌ [UoW] Error persistiendo referido: {e}")
            raise

        print("======================")
        print("📤 Publicando confirmación automática del referido...")
        print("======================")
        
        # Publicar automáticamente VentaReferidaConfirmada
        # Por el momento todos serán confirmados
        despachador = Despachador()
        try:
            datos_confirmacion = {
                'idEvento': comando.idEvento,
                'idReferido': comando.idReferido,
                'idSocio': comando.idSocio,
                'monto': comando.monto * 0.1,  # 10% de comisión por ejemplo
                'tipoEvento': TipoEvento.VENTA.value,
                'fechaEvento': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
            }
            
            despachador.publicar_referido_procesado(datos_confirmacion, estado='confirmado')
            print(f"✅ Referido {comando.idReferido} confirmado automáticamente!")
            
        except Exception as e:
            print(f"❌ Error publicando confirmación automática: {e}")
            # No fallar el procesamiento principal por problemas de publicación

@comando.register(GenerarReferidoCommand)
def ejecutar_comando_generar_referido(comando: GenerarReferidoCommand):
    """
    Registro del comando en el dispatcher
    """
    print(f"Ejecutando GenerarReferidoCommand para evento: {comando.idEvento}")
    handler = GenerarReferidoHandler()
    handler.handle(comando)