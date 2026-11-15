import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

IVA = 0.19
URL = os.environ["APPS_SCRIPT_URL"]
CLAVE = os.environ["SHEET_CLAVE"]


def num(v, defecto=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return defecto


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/productos', methods=['GET'])
def obtener_productos():
    try:
        r = requests.get(URL, params={'clave': CLAVE}, timeout=20)
        filas = r.json()
    except Exception as e:
        return jsonify({'error': 'No se pudo leer la hoja: ' + str(e)}), 502

    if isinstance(filas, dict):
        return jsonify(filas), 502

    productos = []
    for f in filas:
        # Normaliza encabezados: "Precio Base" -> "precio_base"
        f = {str(k).strip().lower().replace(' ', '_'): v for k, v in f.items()}
        cantidad = int(num(f.get('cantidad')))
        productos.append({
            'id': str(f.get('id', '')),
            'nombre': f.get('nombre', ''),
            'cantidad': cantidad,
            'precio_base': num(f.get('precio_base')),
            'iva': num(f.get('iva')),
            'precio_total': num(f.get('precio_total')),
            'fecha_compra': str(f.get('fecha_compra', '')),
            'fecha_venta': str(f.get('fecha_venta', '')),
            'agotado': cantidad <= 0
        })
    return jsonify(productos)


@app.route('/api/productos', methods=['POST'])
def agregar_producto():
    datos = request.json
    try:
        cantidad = int(datos.get('cantidad'))
        precio_base = float(datos.get('precio'))
    except (TypeError, ValueError):
        return jsonify({'error': 'Datos inválidos'}), 400

    iva = precio_base * IVA
    precio_total = precio_base + iva
    agotado = cantidad <= 0

    nuevo_producto = {
        'id': datos.get('id'),
        'nombre': datos.get('nombre'),
        'cantidad': cantidad,
        'precio_base': precio_base,
        'iva': iva,
        'precio_total': precio_total,
        'fecha_compra': datos.get('fecha_compra'),
        'fecha_venta': datos.get('fecha_venta'),
        'agotado': agotado
    }
