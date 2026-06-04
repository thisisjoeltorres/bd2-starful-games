# 📦 Nexus Games: Sistema Web de Inventario y Ventas

Aplicación web desarrollada con **Flask + PostgreSQL** para administrar el inventario físico de videojuegos por plataforma, registrar ventas en tiempo real y generar reportes financieros. Proyecto académico adaptado para la asignatura de Bases de Datos.

## 🎯 Objetivo

Construir un sistema CRUD completo que integre un backend en Python con una base de datos relacional, aplicando vistas SQL para reportes, funciones de agregación, procedimientos almacenados y un trigger automatizado para el control estricto de existencias físicas.

## 🛠️ Tecnologías

| Capa | Tecnología |
| --- | --- |
| **Frontend** | HTML5, CSS3, Bootstrap 5, Bootswatch (Tema personalizado)

 |
| **Backend** | Python 3.12+, Flask

 |
| **Base de datos** | PostgreSQL (Principal) / Estructura compatible con MySQL

 |
| **Reportes** | ReportLab (Generación nativa de PDFs)

 |

---

## 📁 Estructura del Proyecto

```text
nexus_games/
│
├── app.py                  # Punto de entrada y enrutamiento Flask[cite: 1]
├── config.py               # Parámetros de conexión y variables de entorno[cite: 1]
├── requirements.txt        # Dependencias del entorno de ejecución[cite: 1]
│
├── database/
│   ├── conexion.py         # Módulo de conexión a la base de datos[cite: 1]
│   └── nexus_games.sql     # Script DDL (Tablas, Triggers, Vistas y Datos iniciales)[cite: 1]
│
├── controllers/
│   ├── usuario_controller.py   # Lógica de autenticación del personal[cite: 1]
│   ├── juego_controller.py     # Lógica CRUD de videojuegos y stock físico[cite: 1]
│   └── venta_controller.py     # Procesamiento de transacciones de salida[cite: 1]
│
├── templates/
│   ├── login.html          # Control de acceso al sistema[cite: 1]
│   ├── inicio.html         # Panel de control principal (Dashboard)[cite: 1]
│   ├── juegos.html         # Interfaz CRUD del catálogo por plataforma[cite: 1]
│   ├── ventas.html         # Panel para registrar salidas de stock[cite: 1]
│   └── reportes.html       # Visualización de métricas y auditoría[cite: 1]
│
├── static/
│   ├── css/
│   │   └── estilos.css     # Hoja de estilos de la interfaz[cite: 1]
│   ├── img/                # Recursos gráficos y carátulas de muestra[cite: 1]
│   └── pdf/                # Almacenamiento temporal de reportes (gitignored)[cite: 1]
│
└── reports/
    └── generar_pdf.py      # Plantillas de renderizado de reportes a PDF[cite: 1]

```

---

## ⚙️ Instalación y Configuración

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd nexus_games

```

### 2. Crear entorno virtual e instalar dependencias



```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt

```

### 3. Configurar la Base de Datos

Edita el archivo `config.py` e introduce las credenciales correspondientes a tu servidor local:

```python
DB_HOST     = "localhost"
DB_PORT     = 5432          
DB_NAME     = "nexus_games_db"
DB_USER     = "tu_usuario"
DB_PASSWORD = "tu_contraseña"

```

Ejecuta el script SQL en tu gestor o terminal para estructurar la base de datos:

```bash
psql -U tu_usuario -d nexus_games_db -f database/nexus_games.sql

```

### 4. Ejecutar la aplicación

```bash
python app.py

```

Abre en tu navegador de preferencia: `http://localhost:5000`

---

## 🗄️ Modelo de Base de Datos

### Tablas Principales

* **`usuarios`**: Datos de acceso para el personal administrativo o cajeros.
* **`juegos`**: Fichas técnicas del catálogo base (Título, Género, Precio estándar).
* **`plataformas`**: Listado de consolas físicas soportadas (PS5, Xbox Series X, Nintendo Switch, PC).
* **`inventario`**: Tabla pivot que vincula un videojuego con una plataforma específica y almacena su stock físico disponible.
* **`ventas`**: Encabezado global de cada transacción de compra realizada.
* **`detalle_venta`**: Desglose de los ítems adquiridos en una misma venta (Juego + Plataforma, cantidad, precio cobrado).

### Objetos de Base de Datos Avanzados Implementados

* **Vistas SQL (`v_reporte_ventas_detallado`)**: Consolida la información de transacciones mediante `JOINs` limpios para alimentar la interfaz y el módulo PDF de forma óptima.

* **Triggers (`tg_descontar_stock_venta`)**: Ejecuta una rutina automática antes de registrar cada línea de detalle, validando que existan copias físicas suficientes y restándolas del inventario final.

---

## 📐 Convenciones del Proyecto

* **Base de Datos**: Identificadores y atributos escritos en `snake_case` y en minúsculas (`id_juego`, `nombre_plataforma`).


* **Scripts Python**: Organización modular en minúsculas y uso de sufijos semánticos (`juego_controller.py`).


* **Vistas HTML**: Nombres planos en minúsculas y representativos de la funcionalidad (`juegos.html`).


* **Rutas Flask**: Estructura de navegación en formato `kebab-case` (`/juegos/nuevo`, `/ventas/registrar`).

---

## 👤 Autor

Proyecto académico desarrollado para la asignatura de **Bases de Datos 2**.

* **Tiempo límite de desarrollo**: Dos semanas.

## 📝 Licencia

Uso académico interno controlado. No redistribuir sin previa autorización.