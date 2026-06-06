import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

def crear_pdf_reporte(transacciones):
    # Aseguramos que la carpeta temporal exista
    os.makedirs('static/pdf', exist_ok=True)
    ruta_pdf = 'static/pdf/reporte_ventas.pdf'
    
    doc = SimpleDocTemplate(ruta_pdf, pagesize=letter)
    elementos = []
    estilos = getSampleStyleSheet()
    
    # Título del documento
    titulo = Paragraph("Reporte General de Ventas - Starful Games", estilos['Title'])
    elementos.append(titulo)
    elementos.append(Spacer(1, 12))
    
    # Encabezados de la tabla
    datos_tabla = [['ID', 'Fecha', 'Vendedor', 'Videojuego', 'Consola', 'Cant.', 'Total']]
    
    # Llenar la tabla con los datos de la base de datos
    for t in transacciones:
        fecha_str = t['fecha'].strftime("%Y-%m-%d %H:%M") if t['fecha'] else ""
        datos_tabla.append([
            str(t['id_venta']),
            fecha_str,
            str(t['vendedor']),
            str(t['videojuego']),
            str(t['plataforma']),
            str(t['cantidad']),
            f"${t['subtotal']:,.2f}"
        ])
        
    # Darle estilo visual a la tabla
    tabla = Table(datos_tabla)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ECF0F1')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elementos.append(tabla)
    doc.build(elementos)
    
    return ruta_pdf