import os
import traceback
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

IVA = 0.19
URL = os.environ.get("APPS_SCRIPT_URL", "")
CLAVE = os.environ.get("SHEET_CLAVE", "")


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
        if not URL or not CLAVE:
            return jsonify({'error': 'Faltan las variables APPS_SCRIPT_URL o SHEET_CLAVE'}), 500

        r = requests.get(URL, params={'clave': CLAVE}, timeout=30)
        filas = r.json()

        if isinstance(filas, dict):
            return jsonify(filas), 502

        productos = []
        for f in filas:
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
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'Lectura: ' + repr(e)}), 500


@app.route('/api/productos', methods=['POST'])
def agregar_producto():
    try:
        if not URL or not CLAVE:
            return jsonify({'error': 'Faltan las variables APPS_SCRIPT_URL o SHEET_CLAVE'}), 500

        datos = request.get_json(force=True)
        cantidad = int(datos.get('cantidad'))
        precio_base = float(datos.get('precio'))

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

        r = requests.post(URL, json={**nuevo_producto, 'clave': CLAVE}, timeout=30)
        respuesta = r.json()
        if not respuesta.get('ok'):
            return jsonify({'error': 'La hoja respondió: ' + str(respuesta)}), 502

        return jsonify({'mensaje': 'Éxito', 'producto': nuevo_producto}), 201
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'Guardado: ' + repr(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
