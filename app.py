from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from controllers import juego_controller, venta_controller

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

@app.route('/ventas', methods=['GET', 'POST'])
def ventas():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        # Lógica para capturar formulario de ventas enviada al controller
        pass
        
    lista_juegos_disponibles = juego_controller.listar_juegos_disponibles()
    return render_template('ventas.html', productos=lista_juegos_disponibles)

@app.route('/reportes')
def reportes():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    # Lista vacía temporal para que renderice sin conectarse a la BD todavía
    transacciones = [] 
    
    return render_template('reportes.html', transacciones=transacciones)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)