from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from config import Config
from controllers import juego_controller, venta_controller
from reports import generar_pdf

app = Flask(__name__)
app.config.from_object(Config)

# --- Filtro personalizado para formatear moneda en pesos colombianos ---
@app.template_filter('currency')
def format_currency(value):
    return f"${value:,.2f}"

@app.route('/')
def index():
    if 'usuario_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Simulación de validación (Integrar con usuario_controller después)
        if username == 'admin' and password == 'admin123':
            session['usuario_id'] = 1
            session['usuario_nombre'] = 'Administrador Starful'
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciales incorrectas', 'danger')
            
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    return render_template('inicio.html')

@app.route('/juegos')
def juegos():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    lista_juegos = juego_controller.listar_juegos_inventario()
    return render_template('juegos.html', juegos=lista_juegos)

@app.route('/juegos/nuevo', methods=['POST'])
def nuevo_juego():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
        
    # Capturamos los datos que llegan del formulario HTML
    titulo = request.form['titulo']
    genero = request.form['genero']
    id_plataforma = request.form['id_plataforma']
    precio = request.form['precio']
    stock = request.form['stock']
    
    # Llamamos a nuestro controlador para guardar en BD
    exito = juego_controller.registrar_juego(titulo, genero, id_plataforma, precio, stock)
    
    if exito:
        flash('Videojuego físico agregado al inventario exitosamente.', 'success')
    else:
        flash('Ocurrió un error al intentar guardar el videojuego.', 'danger')
        
    # Redirigimos de vuelta a la pantalla de inventario
    return redirect(url_for('juegos'))

@app.route('/juegos/editar/<int:id_inventario>')
def editar_juego(id_inventario):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    # Buscamos el juego en la BD
    juego = juego_controller.obtener_juego_por_id(id_inventario)
    
    if not juego:
        flash('El videojuego solicitado no existe en el inventario.', 'danger')
        return redirect(url_for('juegos'))
        
    return render_template('editar_juego.html', juego=juego)

@app.route('/juegos/actualizar/<int:id_inventario>', methods=['POST'])
def actualizar_juego(id_inventario):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
        
    # Capturamos los datos actualizados del formulario
    id_juego = request.form['id_juego'] # Campo oculto necesario para el UPDATE
    titulo = request.form['titulo']
    genero = request.form['genero']
    id_plataforma = request.form['id_plataforma']
    precio = request.form['precio']
    stock = request.form['stock']
    
    # Enviamos a la BD
    exito = juego_controller.actualizar_juego(id_inventario, id_juego, titulo, genero, id_plataforma, precio, stock)
    
    if exito:
        flash('Videojuego actualizado exitosamente.', 'success')
    else:
        flash('Ocurrió un error al actualizar el videojuego.', 'danger')
        
    return redirect(url_for('juegos'))

@app.route('/juegos/eliminar/<int:id_inventario>')
def eliminar_juego(id_inventario):
    # Validamos que el usuario esté logueado
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
        
    # Llamamos al controlador para ejecutar el DELETE
    exito = juego_controller.eliminar_juego(id_inventario)
    
    # Notificamos al usuario según el resultado
    if exito:
        flash('El videojuego fue retirado del inventario exitosamente.', 'success')
    else:
        flash('Ocurrió un error al intentar eliminar el videojuego.', 'danger')
        
    # Recargamos la vista de la tabla
    return redirect(url_for('juegos'))

@app.route('/ventas', methods=['GET', 'POST'])
def ventas():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        # Capturamos los datos enviados desde el formulario
        id_inventario = request.form['id_inventario']
        cantidad = request.form['cantidad']
        id_usuario = session['usuario_id'] # El ID del cajero que inició sesión
        
        # Procesamos la venta
        exito, mensaje = venta_controller.registrar_venta(id_usuario, id_inventario, cantidad)
        
        if exito:
            flash(mensaje, 'success')
        else:
            # Mostramos el error (Si el stock no alcanza, el Trigger de Postgres manda el texto aquí)
            flash(f'No se pudo completar la venta: {mensaje}', 'danger')
            
        return redirect(url_for('ventas'))
        
    lista_juegos_disponibles = juego_controller.listar_juegos_disponibles()
    return render_template('ventas.html', productos=lista_juegos_disponibles)

@app.route('/reportes')
def reportes():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    # ¡Ahora sí llamamos a la base de datos!
    transacciones = venta_controller.obtener_reporte_ventas() 
    
    return render_template('reportes.html', transacciones=transacciones)

@app.route('/reportes/exportar/pdf')
def exportar_pdf():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    # 1. Traemos los datos de la base de datos
    transacciones = venta_controller.obtener_reporte_ventas()
    
    # 2. Le pasamos los datos a ReportLab para que dibuje el PDF
    ruta_archivo = generar_pdf.crear_pdf_reporte(transacciones)
    
    # 3. Forzamos la descarga del archivo en el navegador
    return send_file(ruta_archivo, as_attachment=True, download_name="Reporte_Starful_Games.pdf")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)