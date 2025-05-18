from flask import Blueprint, render_template, request, redirect, url_for, session
from .services import get_supabase_client

main = Blueprint('main', __name__)

# Verifica que haya un cliente en sesión
def cliente_requerido():
    if 'cliente' not in session:
        return redirect(url_for('main.login'))
    return None

# Muestra la página de inicio
@main.route('/')
def home():
    if 'cliente' in session:
        return redirect(url_for('main.mostrar_productos'))
    return render_template('home.html')

# Permite registrar un nuevo cliente o vendedor
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

# Permite que un cliente inicie sesión
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

# Permite cerrar la sesión actual
@main.route('/logout')
def logout():
    session.pop('cliente', None)
    return redirect(url_for('main.home'))

# Muestra el listado de productos disponibles
@main.route('/productos')
def mostrar_productos():
    if cliente_requerido(): return cliente_requerido()
    supabase = get_supabase_client()
    response = supabase.table('productos').select('*').execute()
    productos = response.data or []
    return render_template('productos.html', productos=productos)

# Agrega un producto al carrito del cliente
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

# Muestra el carrito actual del cliente
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

# Muestra el resumen de la compra con el total
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

# Procesa y confirma la compra del cliente
@main.route('/confirmar_compra', methods=['POST'])
def confirmar_compra():
    if 'cliente' not in session:
        return redirect(url_for('main.login'))

    supabase = get_supabase_client()
    cliente = session['cliente']
    carrito_ids = cliente.get('carrito_compras', [])
    if not carrito_ids:
        return "Tu carrito está vacío."

    productos = []
    total_compra = 0
    for producto_id in carrito_ids:
        response = supabase.table('productos').select('*').eq('id', producto_id).execute()
        if response.data:
            producto = response.data[0]
            if producto['existencias'] <= 0:
                return f"El producto '{producto['nombre_producto']}' no tiene existencias."
            productos.append(producto)
            total_compra += float(producto['precio'])

    if float(cliente['dinero']) < total_compra:
        return f"No tienes suficiente dinero. Total: {total_compra}, Tu saldo: {cliente['dinero']}"

    for producto in productos:
        nuevas_existencias = producto['existencias'] - 1
        supabase.table('productos').update({'existencias': nuevas_existencias}).eq('id', producto['id']).execute()

    nuevo_saldo = float(cliente['dinero']) - total_compra
    historial = cliente.get('historial_compras', [])
    historial.append({'productos': carrito_ids, 'total': total_compra})

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

# Muestra el historial de compras del cliente
@main.route('/historial')
def ver_historial():
    if cliente_requerido(): return cliente_requerido()
    cliente = session['cliente']
    historial = cliente.get('historial_compras', [])
    return render_template('historial.html', historial=historial)

# Permite quitar un producto del carrito
@main.route('/quitar/<int:producto_id>')
def quitar_del_carrito(producto_id):
    if 'cliente' not in session:
        return redirect(url_for('main.login'))

    supabase = get_supabase_client()
    cliente = session['cliente']
    carrito_actual = cliente.get('carrito_compras', [])

    if producto_id in carrito_actual:
        carrito_actual.remove(producto_id)

    supabase.table('clientes').update({'carrito_compras': carrito_actual}).eq('id', cliente['id']).execute()
    cliente['carrito_compras'] = carrito_actual
    session['cliente'] = cliente

    return redirect(url_for('main.ver_carrito'))

# Permite recargar el saldo del cliente
@main.route('/recargar', methods=['GET', 'POST'])
def recargar_dinero():
    if 'cliente' not in session:
        return redirect(url_for('main.login'))

    supabase = get_supabase_client()
    cliente = session['cliente']

    if request.method == 'POST':
        monto = float(request.form['monto'])
        nuevo_saldo = float(cliente['dinero']) + monto

        supabase.table('clientes').update({'dinero': nuevo_saldo}).eq('id', cliente['id']).execute()
        cliente['dinero'] = nuevo_saldo
        session['cliente'] = cliente

        return redirect(url_for('main.mostrar_productos'))

    return render_template('recargar.html', saldo=cliente['dinero'])

# Muestra el panel para que el vendedor gestione sus productos
@main.route('/vendedor', methods=['GET', 'POST'])
def panel_vendedor():
    if 'cliente' not in session or session['cliente'].get('rol') != 'vendedor':
        return redirect(url_for('main.login'))

    supabase = get_supabase_client()
    vendedor_id = session['cliente']['id']

    if request.method == 'POST':
        nombre_producto = request.form['nombre_producto']
        descripcion = request.form['descripcion']
        precio = float(request.form['precio'])
        existencias = int(request.form['existencias'])

        producto_data = {
            'nombre_producto': nombre_producto,
            'descripcion': descripcion,
            'precio': precio,
            'existencias': existencias,
            'vendedor_id': vendedor_id
        }

        supabase.table('productos').insert(producto_data).execute()
        return redirect(url_for('main.panel_vendedor'))

    response = supabase.table('productos').select('*').eq('vendedor_id', vendedor_id).execute()
    mis_productos = response.data or []

    return render_template('vendedor.html', productos=mis_productos)
