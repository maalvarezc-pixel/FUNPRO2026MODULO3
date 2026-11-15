import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

IVA = 0.19
URL = os.environ["APPS_SCRIPT_URL"]
CLAVE = os.environ["SHEET_CLAVE"]


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/productos', methods=['GET'])
def obtener_productos():
    try:
        r = requests.get(URL, params={'clave': CLAVE}, timeout=20)
        filas = r.json()
    except Exception:
        return jsonify({'error': 'No se pudo leer la hoja'}), 502

    if isinstance(filas, dict):
        return jsonify(filas), 502

    productos = []
    for f in filas:
        cantidad = int(f['cantidad'])
        productos.append({
            'id': str(f['id']),
            'nombre': f['nombre'],
            'cantidad': cantidad,
            'precio_base': float(f['precio_base']),
            'iva': float(f['iva']),
            'precio_total': float(f['precio_total']),
            'fecha_compra': f['fecha_compra'],
            'fecha_venta': f['fecha_venta'],
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

    try:
        r = requests.post(URL, json={**nuevo_producto, 'clave': CLAVE}, timeout=20)
        if not r.json().get('ok'):
            return jsonify({'error': 'La hoja rechazó el registro'}), 502
    except Exception:
        return jsonify({'error': 'No se pudo escribir en la hoja'}), 502

    return jsonify({'mensaje': 'Éxito', 'producto': nuevo_producto}), 201


if __name__ == '__main__':
    app.run(debug=True)
