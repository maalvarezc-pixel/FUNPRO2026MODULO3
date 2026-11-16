from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

IVA = 0.19

# Base de datos simulada en memoria (no usa Drive)
inventario = []


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/productos', methods=['GET'])
def obtener_productos():
    return jsonify(inventario)


@app.route('/api/productos', methods=['POST'])
def agregar_producto():
    try:
        datos = request.get_json(force=True)
        cantidad = int(datos.get('cantidad'))
        precio_base = float(datos.get('precio'))
    except (TypeError, ValueError):
        return jsonify({'error': 'Datos inválidos'}), 400

    iva = precio_base * IVA
    precio_total = precio_base + iva

    nuevo_producto = {
        'id': datos.get('id'),
        'nombre': datos.get('nombre'),
        'cantidad': cantidad,
        'precio_base': precio_base,
        'iva': iva,
        'precio_total': precio_total,
        'fecha_compra': datos.get('fecha_compra'),
        'fecha_venta': datos.get('fecha_venta'),
        'agotado': cantidad <= 0
    }

    inventario.append(nuevo_producto)
    return jsonify({'mensaje': 'Éxito', 'producto': nuevo_producto}), 201


if __name__ == '__main__':
    app.run(debug=True)
