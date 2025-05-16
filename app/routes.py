from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from .services import get_supabase_client
from flask import session, flash
from flask import session, redirect, url_for

main = Blueprint('main', __name__)

# Ruta principal
@main.route('/')
def home():
    return 'Bienvenido al e-commerce de Santiago. Accede a /productos o /registro para comenzar.'

# Ruta para listar productos
@main.route('/productos')
def obtener_productos():
    supabase = get_supabase_client()
    response = supabase.table('productos').select('*').execute()
    return jsonify(response.data)

# Ruta para registrar clientes
@main.route('/registro', methods=['GET', 'POST'])
def registro():
    supabase = get_supabase_client()
    if request.method == 'POST':
        nombre = request.form['nombre']
        direccion = request.form['direccion']
        dinero = request.form['dinero']

        cliente_data = {
            'nombre': nombre,
            'direccion': direccion,
            'dinero': float(dinero),
            'carrito_compras': [],
            'historial_compras': []
        }

        response = supabase.table('clientes').insert(cliente_data).execute()

        if response.data:
            return f"Cliente {nombre} registrado exitosamente."
        else:
            return "Error al registrar el cliente."

    return render_template('registro.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    supabase = get_supabase_client()
    if request.method == 'POST':
        nombre = request.form['nombre']
        response = supabase.table('clientes').select('*').eq('nombre', nombre).execute()

        if response.data:
            session['cliente'] = response.data[0]  # Guarda al cliente en sesión
            return f"Bienvenido, {nombre}."
        else:
            return "Cliente no encontrado. Por favor regístrate primero."

    return render_template('login.html')


@main.route('/productos')
def mostrar_productos():
    supabase = get_supabase_client()
    response = supabase.table('productos').select('*').execute()
    productos = response.data or []
    return render_template('productos.html', productos=productos)


@main.route('/agregar_al_carrito/<int:producto_id>')
def agregar_al_carrito(producto_id):
    if 'cliente' not in session:
        return redirect(url_for('main.login'))

    supabase = get_supabase_client()
    cliente = session['cliente']

    # Obtener el carrito actual o inicializarlo vacío
    carrito_actual = cliente.get('carrito_compras', [])

    # Agregar el nuevo producto al carrito
    carrito_actual.append(producto_id)

    # Actualizar en la base de datos
    supabase.table('clientes')\
        .update({'carrito_compras': carrito_actual})\
        .eq('id', cliente['id'])\
        .execute()

    # Actualizar en la sesión
    cliente['carrito_compras'] = carrito_actual
    session['cliente'] = cliente

    return f"Producto {producto_id} agregado al carrito."