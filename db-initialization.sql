
-- Crear bases de datos dedicadas para cada microservicio que usa PostgreSQL
CREATE DATABASE pagos_db;
CREATE DATABASE eventos_db;

-- Otorgar todos los privilegios al usuario por defecto de postgres
GRANT ALL PRIVILEGES ON DATABASE pagos_db TO postgres;
GRANT ALL PRIVILEGES ON DATABASE eventos_db TO postgres;
