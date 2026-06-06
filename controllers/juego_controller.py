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

def registrar_juego(titulo, genero, id_plataforma, precio, stock):
    """Inserta un nuevo título y su stock físico inicial en la BD"""
    conexion = obtener_conexion()
    if conexion:
        try:
            with conexion.cursor() as cursor:
                # 1. Insertamos el juego y pedimos que nos devuelva el ID generado
                query_juego = """
                    INSERT INTO juegos (titulo, genero, precio)
                    VALUES (%s, %s, %s) RETURNING id_juego;
                """
                cursor.execute(query_juego, (titulo, genero, precio))
                id_juego = cursor.fetchone()[0]

                # 2. Insertamos el stock físico atado a la plataforma
                query_inventario = """
                    INSERT INTO inventario (id_juego, id_plataforma, stock)
                    VALUES (%s, %s, %s);
                """
                cursor.execute(query_inventario, (id_juego, id_plataforma, stock))
            
            # Si todo sale bien, guardamos los cambios (Transaction Commit)
            conexion.commit()
            return True
        except Exception as e:
            print(f"Error al registrar videojuego: {e}")
            conexion.rollback() # Cancelamos si hubo un error para no dejar datos a medias
            return False
        finally:
            conexion.close()
    return False