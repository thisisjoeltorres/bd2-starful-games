from database.conexion import obtener_conexion

def listar_juegos_inventario():
    """Trae el listado completo del catálogo físico con su plataforma y stock disponible"""
    conexion = obtener_conexion()
    juegos = []
    if conexion:
        try:
            with conexion.cursor() as cursor:
                query = """
                    SELECT i.id_inventario, j.titulo, j.genero, p.nombre_plataforma, j.precio, i.stock
                    FROM inventario i
                    JOIN juegos j ON i.id_juego = j.id_juego
                    JOIN plataformas p ON i.id_plataforma = p.id_plataforma
                    ORDER BY j.titulo ASC, p.nombre_plataforma ASC;
                """
                cursor.execute(query)
                # Mapeo manual de tuplas si no se usa DictCursor
                columnas = [desc[0] for desc in cursor.description]
                juegos = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
        except Exception as e:
            print(f"Error al listar inventario de videojuegos: {e}")
        finally:
            conexion.close()
    return juegos

def listar_juegos_disponibles():
    """Trae solo los juegos que tienen existencias mayores a 0 para el módulo de ventas"""
    conexion = obtener_conexion()
    juegos = []
    if conexion:
        try:
            with conexion.cursor() as cursor:
                query = """
                    SELECT i.id_inventario, j.titulo, p.nombre_plataforma, j.precio, i.stock
                    FROM inventario i
                    JOIN juegos j ON i.id_juego = j.id_juego
                    JOIN plataformas p ON i.id_plataforma = p.id_plataforma
                    WHERE i.stock > 0;
                """
                cursor.execute(query)
                columnas = [desc[0] for desc in cursor.description]
                juegos = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
        except Exception as e:
            print(f"Error al listar juegos disponibles: {e}")
        finally:
            conexion.close()
    return juegos