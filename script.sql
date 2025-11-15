create database camaleonides;

CREATE TABLE usuarios (
    id_usuario INT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    apellido_paterno VARCHAR(50) NOT NULL,
    apellido_materno VARCHAR(50),
    usuario VARCHAR(30) NOT NULL UNIQUE,
    contraseña VARCHAR(255) NOT NULL,
    rango ENUM('admin', 'gerente', 'operador', 'vendedor') DEFAULT 'operador',
    fecha_registro DATETIME
);

CREATE TABLE alimentos (
    id_alimento INT PRIMARY KEY,
    nombre ENUM('calabaza', 'nopal', 'zanahoria') NOT NULL,
    stock_kg DECIMAL(6,2) NOT NULL DEFAULT 0.00,
    fecha_compra DATE NOT NULL,
    fecha_caducidad DATE,
    proveedor VARCHAR(100)
);


CREATE TABLE insectos_grillos (
    id_insecto INT PRIMARY KEY,
    stock INT NOT NULL DEFAULT 0,
    etapa ENUM('huevo', 'larva', 'adulto') NOT NULL,
    fecha_puesta DATE,
    fecha_eclosion DATE,
    id_lote VARCHAR(20),
    fecha_registro DATETIME
);

CREATE TABLE insectos_cucarachas (
    id_insecto INT PRIMARY KEY,
    stock INT NOT NULL DEFAULT 0,
    etapa ENUM('huevo', 'larva', 'adulto') NOT NULL,
    fecha_puesta DATE,
    fecha_eclosion DATE,
    id_lote VARCHAR(20),
    fecha_registro DATETIME
);

CREATE TABLE insectos_zophobas (
    id_insecto INT PRIMARY KEY,
    stock INT NOT NULL DEFAULT 0,
    etapa ENUM('huevo', 'larva', 'adulto') NOT NULL,
    fecha_puesta DATE,
    fecha_eclosion DATE,
    id_lote VARCHAR(20),
    fecha_registro DATETIME
);

CREATE TABLE insectos_tenebrios (
    id_insecto INT PRIMARY KEY,
    stock INT NOT NULL DEFAULT 0,
    etapa ENUM('huevo', 'larva', 'adulto') NOT NULL,
    fecha_puesta DATE,
    fecha_eclosion DATE,
    id_lote VARCHAR(20),
    fecha_registro DATETIME
);

CREATE TABLE ventas (
    id_venta INT PRIMARY KEY,
    id_insecto INT NOT NULL,
    especie ENUM('grillo', 'cucaracha', 'zophobas', 'tenebrio') NOT NULL,
    cliente ENUM('Petco') DEFAULT 'Petco',
    cantidad INT NOT NULL,
    etapa ENUM('huevo', 'ninfa', 'larva', 'adulto') NOT NULL,
    fecha_salida DATE NOT NULL,
    fecha_entrega DATE,
    estado ENUM('pendiente', 'enviado', 'entregado', 'cancelado') DEFAULT 'pendiente',
    id_usuario INT,
    fecha_registro DATETIME,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

INSERT INTO usuarios (id_usuario, nombre, apellido_paterno, apellido_materno, usuario, contraseña, rango) VALUES
(1, 'Ana', 'López', 'García', 'ana.lopez', 'ana2025!', 'admin'),
(2, 'Carlos', 'Méndez', 'Ruiz', 'carlos.m', 'carlos2025!', 'vendedor'),
(3, 'María', 'Pérez', 'Hernández', 'maria.p', 'maria2025!', 'operador');

-- insectos_grillos (3)
INSERT INTO insectos_grillos (id_insecto, stock, etapa, fecha_puesta, fecha_eclosion, id_lote) VALUES
(1, 12000, 'adulto', '2025-08-01', '2025-08-20', 'GRI-2025-01'),
(2, 8000, 'larva', '2025-08-15', '2025-09-05', 'GRI-2025-02'),
(3, 5000, 'huevo', '2025-09-01', '2025-10-10', 'GRI-2025-03');


INSERT INTO insectos_cucarachas (id_insecto, stock, etapa, fecha_puesta, fecha_eclosion, id_lote) VALUES
(1, 6000, 'adulto', '2025-07-20', '2025-08-10', 'CUC-2025-01'),
(2, 4000, 'larva', '2025-08-10', '2025-08-30', 'CUC-2025-02'),
(3, 2000, 'huevo', '2025-09-05', '2025-09-01', 'CUC-2025-03');

INSERT INTO insectos_zophobas (id_insecto, stock, etapa, fecha_puesta, fecha_eclosion, id_lote) VALUES
(1, 9000, 'larva', '2025-07-25', '2025-08-05', 'ZOP-2025-01'),
(2, 7000, 'adulto', '2025-07-15', '2025-08-05', 'ZOP-2025-02'),
(3, 3000, 'huevo', '2025-08-25', '2025-08-15', 'ZOP-2025-03');

INSERT INTO insectos_tenebrios (id_insecto, stock, etapa, fecha_puesta, fecha_eclosion, id_lote) VALUES
(1, 11000, 'adulto', '2025-08-05', '2025-08-25', 'TEN-2025-01'),
(2, 6000, 'larva', '2025-08-20', '2025-09-10', 'TEN-2025-02'),
(3, 4000, 'huevo', '2025-09-10', '2025-09-21', 'TEN-2025-03');

INSERT INTO ventas (id_venta, id_insecto, especie, cantidad, etapa, fecha_salida, id_usuario) VALUES
(1, 1, 'grillo', 2000, 'adulto', '2025-09-15', 1),
(2, 1, 'cucaracha', 1000, 'adulto', '2025-09-16', 2),
(3, 1, 'zophobas', 1500, 'larva', '2025-09-17', 1),
(4, 1, 'tenebrio', 3000, 'adulto', '2025-09-18', 1),
(5, 1, 'grillo', 2500, 'adulto', '2025-09-19', 2),
(6, 1, 'cucaracha', 800, 'adulto', '2025-09-20', 1),
(7, 1, 'zophobas', 2000, 'larva', '2025-09-21', 2),
(8, 1, 'tenebrio', 4000, 'larva', '2025-09-22', 1),
(9, 1, 'grillo', 1500, 'adulto', '2025-09-23', 2),
(10, 1, 'cucaracha', 1200, 'adulto', '2025-09-24', 1);
