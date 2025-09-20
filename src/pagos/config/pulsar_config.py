from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración principal del microservicio de pagos.

    Usa Pydantic BaseSettings para permitir sobreescritura por variables de entorno.
    Mantiene nombres en MAYÚSCULAS para convenciones de configuración.
    """
    DB_URL: str = "postgresql+psycopg2://postgres:postgres@postgres-pagos:5432/pagos_db"
    PULSAR_URL: str = "pulsar://pulsar:6650"
    SERVICE_NAME: str = "pagos-api"
    TOPIC_PAGOS: str = "eventos-pago"  # Unificado a singular según contrato
    TOPIC_REFERIDO_CONFIRMADO: str = "eventos-referido-confirmado"
    OUTBOX_BATCH_SIZE: int = 100  # Ya no se usa, dejado por compatibilidad

    class Config:
        env_file = ".env"


settings = Settings()


class PulsarConfig:
    """Wrapper de compatibilidad retro.

    Código legado (consumer/tests) importaba PulsarConfig y esperaba atributos en minúscula.
    Esta clase adapta la nueva `Settings` al contrato anterior para evitar refactors masivos.
    Futuro: reemplazar imports de PulsarConfig por `from config.pulsar_config import settings`.
    """

    def __init__(self):
        # Atributos legacy en minúscula
        self.pulsar_url = settings.PULSAR_URL
        # Exponer también los tópicos usados
        self.topic_pagos = settings.TOPIC_PAGOS
        self.topic_referido_confirmado = settings.TOPIC_REFERIDO_CONFIRMADO

    def __repr__(self) -> str:  # útil para debugging
        return (
            f"PulsarConfig(pulsar_url={self.pulsar_url}, "
            f"topic_pagos={self.topic_pagos}, "
            f"topic_referido_confirmado={self.topic_referido_confirmado})"
        )


__all__ = ["settings", "Settings", "PulsarConfig"]
