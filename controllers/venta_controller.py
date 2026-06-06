from database.conexion import obtener_conexion

def registrar_venta(id_usuario, id_inventario, cantidad):
    """Procesa la transacción y deja que el Trigger actualice el stock"""
    conexion = obtener_conexion()
    if conexion:
        try:
            with conexion.cursor() as cursor:
                # 1. Obtener el precio unitario del juego desde la BD
                query_precio = """
                    SELECT j.precio 
                    FROM inventario i
                    JOIN juegos j ON i.id_juego = j.id_juego
                    WHERE i.id_inventario = %s;
                """
                cursor.execute(query_precio, (id_inventario,))
                resultado = cursor.fetchone()
                
                if not resultado:
                    return False, "El videojuego seleccionado no existe."
                
                precio_unitario = resultado[0]
                total_venta = precio_unitario * int(cantidad)

                # 2. Insertar el encabezado de la Venta (Retorna el ID generado)
                query_venta = """
                    INSERT INTO ventas (id_usuario, total)
                    VALUES (%s, %s) RETURNING id_venta;
                """
                cursor.execute(query_venta, (id_usuario, total_venta))
                id_venta = cursor.fetchone()[0]

                # 3. Insertar el Detalle de Venta (¡AQUÍ SE ACTIVA EL TRIGGER DE STOCK!)
                query_detalle = """
                    INSERT INTO detalle_venta (id_venta, id_inventario, cantidad, precio_unitario)
                    VALUES (%s, %s, %s, %s);
                """
                cursor.execute(query_detalle, (id_venta, id_inventario, cantidad, precio_unitario))

            # Si todo salió perfecto, confirmamos los cambios en la BD
            conexion.commit()
            return True, "Transacción procesada y stock actualizado exitosamente."
            
        except Exception as e:
            # Si el Trigger detecta que no hay stock, o hay otro error, deshacemos todo
            conexion.rollback()
            return False, str(e)
        finally:
            conexion.close()
            
    return False, "Error crítico de conexión a la base de datos."