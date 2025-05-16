from flask import Blueprint, jsonify
from .services import get_supabase_client

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return 'Hola Santiago, Flask está funcionando correctamente 🎉'

@main.route('/productos')
def obtener_productos():
    supabase = get_supabase_client()
    response = supabase.table('productos').select('*').execute()

    if response.data:
        return jsonify(response.data)
    else:
        return jsonify({"message": "No se encontraron productos o la tabla está vacía."}), 404
