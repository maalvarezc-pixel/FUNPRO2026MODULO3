from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Simulación de base de datos en memoria
inventario = []

@app.route('/')
def index():
    # Sirve el archivo HTML del frontend
    return render_template('index.html')

@app.route('/api/productos', methods=['POST'])
def agregar_producto():
    datos = request.json
    
    id_prod = datos.get('id')
    nombre = datos.get('nombre')
    cantidad = int(datos.get('cantidad'))
    precio_base = float(datos.get('precio'))
    fecha_compra = datos.get('fecha_compra')
    fecha_venta = datos.get('fecha_venta')
    
    # REQUERIMIENTO: Cálculo del IVA (19%) en el Backend
    iva = precio_base * 0.19
    precio_total = precio_base + iva
    
    # REQUERIMIENTO: Informar cuando un producto se haya agotado
    agotado = True if cantidad <= 0 else False
    
    nuevo_producto = {
        'id': id_prod,
        'nombre': nombre,
        'cantidad': cantidad,
        'precio_base': precio_base,
        'iva': iva,
        'precio_total': precio_total,
        'fecha_compra': fecha_compra,
        'fecha_venta': fecha_venta,
        'agotado': agotado
    }
    
    inventario.append(nuevo_producto)
    return jsonify({'mensaje': 'Éxito', 'producto': nuevo_producto}), 201

@app.route('/api/productos', methods=['GET'])
def obtener_productos():
    return jsonify(inventario)

if __name__ == '__main__':
    app.run(debug=True)
