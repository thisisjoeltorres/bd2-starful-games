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

def obtener_reporte_ventas():
    """Obtiene el historial completo de ventas desde la vista SQL"""
    conexion = obtener_conexion()
    transacciones = []
    if conexion:
        try:
            with conexion.cursor() as cursor:
                # Consultamos la vista que ya creamos en PostgreSQL
                query = "SELECT * FROM v_reporte_ventas_detallado ORDER BY fecha DESC;"
                cursor.execute(query)
                columnas = [desc[0] for desc in cursor.description]
                transacciones = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
        except Exception as e:
            print(f"Error al obtener reporte de ventas: {e}")
        finally:
            conexion.close()
    return transacciones

def obtener_datos_dashboard():
    """Recupera los contadores de control de inventario y los movimientos más recientes"""
    conexion = obtener_conexion()
    
    # Inicializamos una estructura por defecto en caso de fallo de conexión
    datos = {
        'total_juegos': 0,
        'ventas_hoy': 0,
        'stock_critico': 0,
        'ultimos_movimientos': []
    }
    
    if conexion:
        try:
            with conexion.cursor() as cursor:
                # 1. Total de títulos registrados en el catálogo base
                cursor.execute("SELECT COUNT(*) FROM juegos;")
                datos['total_juegos'] = cursor.fetchone()[0]

                # 2. Total de transacciones de salida (Ventas) realizadas el día de hoy
                cursor.execute("SELECT COUNT(*) FROM ventas WHERE fecha::date = CURRENT_DATE;")
                datos['ventas_hoy'] = cursor.fetchone()[0]

                # 3. Cantidad de ítems en almacén cuyo stock físico es de 3 unidades o menos
                cursor.execute("SELECT COUNT(*) FROM inventario WHERE stock <= 3;")
                datos['stock_critico'] = cursor.fetchone()[0]

                # 4. Obtener los últimos 5 movimientos reales desde nuestra vista detallada
                query_movimientos = """
                    SELECT videojuego, plataforma 
                    FROM v_reporte_ventas_detallado 
                    ORDER BY fecha DESC 
                    LIMIT 5;
                """
                cursor.execute(query_movimientos)
                
                # Mapeamos los resultados construyendo el estado como 'Salida (Venta)'
                datos['ultimos_movimientos'] = [
                    {'videojuego': fila[0], 'plataforma': fila[1], 'estado': 'Salida (Venta)'}
                    for fila in cursor.fetchall()
                ]
                
        except Exception as e:
            print(f"Error al recopilar métricas del dashboard: {e}")
        finally:
            conexion.close()
            
    return datos