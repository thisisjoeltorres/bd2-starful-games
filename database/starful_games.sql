-- =============================================================================
-- 1. CREACIÓN DE TABLAS (Convención snake_case)
-- =============================================================================

CREATE TABLE usuarios (
    id_usuario SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    nombre VARCHAR(100) NOT NULL
);

CREATE TABLE plataformas (
    id_plataforma SERIAL PRIMARY KEY,
    nombre_plataforma VARCHAR(50) UNIQUE NOT NULL -- PS5, Xbox Series X, Nintendo Switch, PC
);

CREATE TABLE juegos (
    id_juego SERIAL PRIMARY KEY,
    titulo VARCHAR(150) NOT NULL,
    genero VARCHAR(50),
    precio DECIMAL(10, 2) NOT NULL
);

-- Tabla intermedia que maneja el inventario físico real por plataforma
CREATE TABLE inventario (
    id_inventario SERIAL PRIMARY KEY,
    id_juego INT REFERENCES juegos(id_juego) ON DELETE CASCADE,
    id_plataforma INT REFERENCES plataformas(id_plataforma) ON DELETE CASCADE,
    stock INT NOT NULL DEFAULT 0 CHECK (stock >= 0),
    UNIQUE(id_juego, id_plataforma)
);

CREATE TABLE ventas (
    id_venta SERIAL PRIMARY KEY,
    id_usuario INT REFERENCES usuarios(id_usuario),
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total DECIMAL(10,2) DEFAULT 0.00
);

CREATE TABLE detalle_venta (
    id_detalle SERIAL PRIMARY KEY,
    id_venta INT REFERENCES ventas(id_venta) ON DELETE CASCADE,
    id_inventario INT REFERENCES inventario(id_inventario), -- Apesta al item específico (ej: Elden Ring para PS5)
    cantidad INT NOT NULL CHECK (cantidad > 0),
    precio_unitario DECIMAL(10,2) NOT NULL
);

-- =============================================================================
-- 2. LOGIC: TRIGGERS PARA CONTROL DE STOCK FÍSICO
-- =============================================================================

CREATE OR REPLACE FUNCTION fx_actualizar_stock_venta()
RETURNS TRIGGER AS $$
BEGIN
    -- Validar si hay stock suficiente antes de proceder
    IF (SELECT stock FROM inventario WHERE id_inventario = NEW.id_inventario) < NEW.cantidad THEN
        RAISE EXCEPTION 'Stock insuficiente para el videojuego seleccionado en esta plataforma.';
    END IF;

    -- Descontar el stock físico del inventario
    UPDATE inventario
    SET stock = stock - NEW.cantidad
    WHERE id_inventario = NEW.id_inventario;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tg_descontar_stock_venta
BEFORE INSERT ON detalle_venta
FOR EACH ROW
EXECUTE FUNCTION fx_actualizar_stock_venta();

-- =============================================================================
-- 3. VISTAS SQL PARA REPORTES CONSOLIDADOS
-- =============================================================================

CREATE OR REPLACE VIEW v_reporte_ventas_detallado AS
SELECT 
    v.id_venta,
    v.fecha,
    u.nombre AS vendedor,
    j.titulo AS videojuego,
    p.nombre_plataforma AS plataforma,
    dv.cantidad,
    dv.precio_unitario,
    (dv.cantidad * dv.precio_unitario) AS subtotal
FROM detalle_venta dv
JOIN ventas v ON dv.id_venta = v.id_venta
JOIN usuarios u ON v.id_usuario = u.id_usuario
JOIN inventario i ON dv.id_inventario = i.id_inventario
JOIN juegos j ON i.id_juego = j.id_juego
JOIN plataformas p ON i.id_plataforma = p.id_plataforma;

-- =============================================================================
-- 4. DATOS DE PRUEBA (DATA SEEDING)
-- =============================================================================
INSERT INTO usuarios (username, password, nombre) VALUES 
('admin', 'admin123', 'Administrador Starful');

INSERT INTO plataformas (nombre_plataforma) VALUES 
('PlayStation 5'), ('Xbox Series X'), ('Nintendo Switch'), ('PC Digital/Físico');

INSERT INTO juegos (titulo, genero, precio) VALUES 
('The Legend of Zelda: Tears of the Kingdom', 'Aventura', 249000.00),
('Elden Ring', 'RPG / Soulslike', 199000.00),
('Cyberpunk 2077', 'RPG / Ciencia Ficción', 120000.00);

-- Vinculamos stock a plataformas específicas
INSERT INTO inventario (id_juego, id_plataforma, stock) VALUES 
(1, 3, 15), -- Zelda en Switch
(2, 1, 8),  -- Elden Ring en PS5
(2, 2, 5),  -- Elden Ring en Xbox
(3, 1, 4);  -- Cyberpunk en PS5