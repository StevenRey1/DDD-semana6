CREATE TABLE referidos (
    id VARCHAR PRIMARY KEY,
    "idSocio" VARCHAR NOT NULL,
    "idReferido" VARCHAR NOT NULL,
    estado VARCHAR NOT NULL,
    "idEvento" VARCHAR NOT NULL,
    monto FLOAT NOT NULL,
    "tipoEvento" VARCHAR NOT NULL,
    "fechaEvento" TIMESTAMP NOT NULL,
    fecha_creacion TIMESTAMP NOT NULL,
    fecha_actualizacion TIMESTAMP NOT NULL DEFAULT NOW()
);