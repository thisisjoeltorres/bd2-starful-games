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

def obtener_juego_por_id(id_inventario):
    """Busca los datos de un juego específico para llenar el formulario de edición"""
    conexion = obtener_conexion()
    juego = None
    if conexion:
        try:
            with conexion.cursor() as cursor:
                query = """
                    SELECT i.id_inventario, i.id_juego, j.titulo, j.genero, i.id_plataforma, j.precio, i.stock
                    FROM inventario i
                    JOIN juegos j ON i.id_juego = j.id_juego
                    WHERE i.id_inventario = %s;
                """
                cursor.execute(query, (id_inventario,))
                fila = cursor.fetchone()
                if fila:
                    columnas = [desc[0] for desc in cursor.description]
                    juego = dict(zip(columnas, fila))
        except Exception as e:
            print(f"Error al obtener juego por ID: {e}")
        finally:
            conexion.close()
    return juego

def actualizar_juego(id_inventario, id_juego, titulo, genero, id_plataforma, precio, stock):
    """Ejecuta el UPDATE en las tablas juegos e inventario"""
    conexion = obtener_conexion()
    if conexion:
        try:
            with conexion.cursor() as cursor:
                # 1. Actualizar los datos base en la tabla juegos
                query_juego = """
                    UPDATE juegos
                    SET titulo = %s, genero = %s, precio = %s
                    WHERE id_juego = %s;
                """
                cursor.execute(query_juego, (titulo, genero, precio, id_juego))

                # 2. Actualizar plataforma y stock en la tabla inventario
                query_inventario = """
                    UPDATE inventario
                    SET id_plataforma = %s, stock = %s
                    WHERE id_inventario = %s;
                """
                cursor.execute(query_inventario, (id_plataforma, stock, id_inventario))

            conexion.commit()
            return True
        except Exception as e:
            print(f"Error al actualizar videojuego: {e}")
            conexion.rollback()
            return False
        finally:
            conexion.close()
    return False

def eliminar_juego(id_inventario):
    """Elimina un registro específico del inventario físico"""
    conexion = obtener_conexion()
    if conexion:
        try:
            with conexion.cursor() as cursor:
                # Ejecutamos el DELETE solo sobre la tabla inventario
                query = "DELETE FROM inventario WHERE id_inventario = %s;"
                cursor.execute(query, (id_inventario,))
            
            # Confirmamos los cambios
            conexion.commit()
            return True
        except Exception as e:
            print(f"Error al eliminar ítem del inventario: {e}")
            conexion.rollback()
            return False
        finally:
            conexion.close()
    return False