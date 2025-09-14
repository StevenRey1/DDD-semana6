from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_URL: str = "postgresql+psycopg2://pagos:pagos@pagos-db:5432/pagos"
    PULSAR_URL: str = "pulsar://pulsar:6650"
    SERVICE_NAME: str = "pagos-api"
    TOPIC_PAGOS: str = "eventos-pagos"
    TOPIC_REFERIDO_CONFIRMADO: str = "eventos-referido-confirmado"
    OUTBOX_BATCH_SIZE: int = 100
    class Config:
        env_file = ".env"

settings = Settings()
