from flask import Blueprint, render_template, request, redirect, url_for, session
from .services import get_supabase_client

main = Blueprint('main', __name__)

# 🛡️ Función de protección
def cliente_requerido():
    if 'cliente' not in session:
        return redirect(url_for('main.login'))
    return None

# 🏠 Página de inicio
@main.route('/')
def home():
    if 'cliente' in session:
        return redirect(url_for('main.mostrar_productos'))
    return render_template('home.html')

# 👤 Registro
@main.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        supabase = get_supabase_client()
        nombre = request.form['nombre']
        direccion = request.form['direccion']
        dinero = request.form['dinero']
        rol = request.form['rol']

        cliente_data = {
            'nombre': nombre,
            'direccion': direccion,
            'dinero': float(dinero),
            'rol': rol,
            'carrito_compras': [],
            'historial_compras': []
        }

        response = supabase.table('clientes').insert(cliente_data).execute()
        if response.data:
            return redirect(url_for('main.login'))
        return "Error al registrar el usuario."
    return render_template('registro.html')

# 🔑 Inicio de sesión
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        supabase = get_supabase_client()
        nombre = request.form['nombre']
        response = supabase.table('clientes').select('*').eq('nombre', nombre).execute()
        if response.data:
            session['cliente'] = response.data[0]
            return redirect(url_for('main.mostrar_productos'))
        return "Cliente no encontrado. Regístrate primero."
    return render_template('login.html')

# 🚪 Cerrar sesión
@main.route('/logout')
def logout():
    session.pop('cliente', None)
    return redirect(url_for('main.home'))

# 🛒 Listado de productos
@main.route('/productos')
def mostrar_productos():
    if cliente_requerido(): return cliente_requerido()
    supabase = get_supabase_client()
    response = supabase.table('productos').select('*').execute()
    productos = response.data or []
    return render_template('productos.html', productos=productos)

# ➕ Agregar producto al carrito
@main.route('/agregar/<int:producto_id>')
def agregar_al_carrito(producto_id):
    if cliente_requerido(): return cliente_requerido()
    supabase = get_supabase_client()
    cliente = session['cliente']
    carrito_actual = cliente.get('carrito_compras', [])
    carrito_actual.append(producto_id)
    supabase.table('clientes').update({'carrito_compras': carrito_actual}).eq('id', cliente['id']).execute()
    cliente['carrito_compras'] = carrito_actual
    session['cliente'] = cliente
    return redirect(url_for('main.ver_carrito'))

# 🛍️ Ver carrito
@main.route('/carrito')
def ver_carrito():
    if cliente_requerido(): return cliente_requerido()
    supabase = get_supabase_client()
    cliente = session['cliente']
    carrito_ids = cliente.get('carrito_compras', [])
    productos = []
    for producto_id in carrito_ids:
        response = supabase.table('productos').select('*').eq('id', producto_id).execute()
        if response.data:
            productos.append(response.data[0])
    return render_template('carrito.html', carrito=productos)

# ✅ Resumen de compra
@main.route('/comprar')
def mostrar_compra():
    if cliente_requerido(): return cliente_requerido()
    supabase = get_supabase_client()
    cliente = session['cliente']
    carrito_ids = cliente.get('carrito_compras', [])
    productos = []
    total = 0
    for producto_id in carrito_ids:
        response = supabase.table('productos').select('*').eq('id', producto_id).execute()
        if response.data:
            producto = response.data[0]
            productos.append(producto)
            total += float(producto['precio'])
    return render_template('comprar.html', carrito=productos, total=total)

# 💳 Confirmar compra
@main.route('/confirmar_compra', methods=['POST'])
def confirmar_compra():
    if cliente_requerido(): return cliente_requerido()
    supabase = get_supabase_client()
    cliente = session['cliente']
    carrito_ids = cliente.get('carrito_compras', [])
    if not carrito_ids:
        return "Tu carrito está vacío."
    productos = []
    total = 0
    for producto_id in carrito_ids:
        response = supabase.table('productos').select('*').eq('id', producto_id).execute()
        if response.data:
            producto = response.data[0]
            productos.append(producto)
            total += float(producto['precio'])
    if float(cliente['dinero']) < total:
        return f"No tienes suficiente dinero. Total: {total}, Tu saldo: {cliente['dinero']}"
    nuevo_saldo = float(cliente['dinero']) - total
    historial = cliente.get('historial_compras', [])
    historial.append({'productos': carrito_ids, 'total': total})
    supabase.table('clientes').update({
        'dinero': nuevo_saldo,
        'carrito_compras': [],
        'historial_compras': historial
    }).eq('id', cliente['id']).execute()
    cliente['dinero'] = nuevo_saldo
    cliente['carrito_compras'] = []
    cliente['historial_compras'] = historial
    session['cliente'] = cliente
    return redirect(url_for('main.ver_historial'))

# 🧾 Ver historial de compras
@main.route('/historial')
def ver_historial():
    if cliente_requerido(): return cliente_requerido()
    cliente = session['cliente']
    historial = cliente.get('historial_compras', [])
    return render_template('historial.html', historial=historial)

@main.route('/quitar/<int:producto_id>')
def quitar_del_carrito(producto_id):
    if 'cliente' not in session:
        return redirect(url_for('main.login'))

    supabase = get_supabase_client()
    cliente = session['cliente']
    carrito_actual = cliente.get('carrito_compras', [])

    # Eliminar el producto si existe
    if producto_id in carrito_actual:
        carrito_actual.remove(producto_id)

    # Actualizar en la base de datos y en sesión
    supabase.table('clientes').update({'carrito_compras': carrito_actual}).eq('id', cliente['id']).execute()
    cliente['carrito_compras'] = carrito_actual
    session['cliente'] = cliente

    return redirect(url_for('main.ver_carrito'))

@main.route('/recargar', methods=['GET', 'POST'])
def recargar_dinero():
    if 'cliente' not in session:
        return redirect(url_for('main.login'))

    supabase = get_supabase_client()
    cliente = session['cliente']

    if request.method == 'POST':
        monto = float(request.form['monto'])
        nuevo_saldo = float(cliente['dinero']) + monto

        # Actualizar en base de datos
        supabase.table('clientes').update({'dinero': nuevo_saldo}).eq('id', cliente['id']).execute()

        # Actualizar en sesión
        cliente['dinero'] = nuevo_saldo
        session['cliente'] = cliente

        return redirect(url_for('main.mostrar_productos'))

    return render_template('recargar.html', saldo=cliente['dinero'])
@main.route('/vendedor', methods=['GET', 'POST'])
def panel_vendedor():
    if 'cliente' not in session or session['cliente'].get('rol') != 'vendedor':
        return redirect(url_for('main.login'))

    supabase = get_supabase_client()

    if request.method == 'POST':
        nombre_producto = request.form['nombre_producto']
        descripcion = request.form['descripcion']
        precio = float(request.form['precio'])
        existencias = int(request.form['existencias'])

        producto_data = {
            'nombre_producto': nombre_producto,
            'descripcion': descripcion,
            'precio': precio,
            'existencias': existencias
        }

        supabase.table('productos').insert(producto_data).execute()
        return redirect(url_for('main.panel_vendedor'))

    return render_template('vendedor.html')
