# 📦 Proyecto E-commerce con Flask y Supabase

Este proyecto es una **simulación de un e-commerce** que permite a los usuarios:
- Registrarse como **clientes o vendedores**.
- Iniciar sesión y **gestionar su cuenta**.
- **Ver productos**, agregarlos al **carrito**, y **realizar compras**.
- **Recargar saldo** y **ver el historial** de compras.
- Los **vendedores** pueden **gestionar sus productos**.

## 🛠️ Tecnologías Usadas

- **Python 3**
- **Flask**
- **Supabase** (Base de datos como servicio, tipo PostgreSQL)
- **Bootstrap** (opcional, para estilos)
- **Jinja2** (motor de plantillas de Flask)

## 🚀 Instalación y Configuración

### 1. Clona el repositorio

```bash
git clone https://github.com/tu-usuario/tu-repositorio.git
cd tu-repositorio
```

### 2. Instala las dependencias

```bash
pip install flask python-dotenv supabase
```

### 3. Configura las variables de entorno

Crea un archivo **.env** con la configuración de tu **Supabase**:

```
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-clave-secreta
```

## 📂 Estructura del Proyecto

```
/tu-proyecto
│
├── app.py
├── main.py (o blueprints/)
├── services.py
├── templates/
│   ├── home.html
│   ├── registro.html
│   ├── login.html
│   ├── productos.html
│   ├── carrito.html
│   ├── comprar.html
│   ├── historial.html
│   ├── recargar.html
│   └── vendedor.html
├── static/
│   └── (estilos y scripts opcionales)
└── README.md
```

## ⚙️ Cómo Ejecutar

1. Ejecuta la aplicación:

```bash
flask run
```

2. Accede desde tu navegador:

```
http://127.0.0.1:5000/
```

## 🧑‍💻 Funcionalidades

### Cliente
- Registrarse con nombre, dirección y saldo inicial.
- Iniciar sesión.
- Ver productos disponibles.
- Agregar productos al carrito.
- Ver el carrito y realizar la compra.
- Recargar saldo.
- Consultar historial de compras.

### Vendedor
- Registrarse como vendedor.
- Iniciar sesión como vendedor.
- Publicar productos con descripción, precio y existencias.
- Ver sus productos publicados.

## 📝 Notas

- Debes tener tu **Supabase** correctamente configurado.
- Asegúrate de tener las **tablas 'clientes' y 'productos'** en tu base de datos.
- Puedes extender el sistema con **más roles, filtros o reportes**.

## 🧑‍🤝‍🧑 Contribuciones

Si deseas contribuir:
1. Haz un fork del repositorio.
2. Crea una rama (`git checkout -b mejora-x`).
3. Sube los cambios (`git push origin mejora-x`).
4. Abre un Pull Request.

## 📄 Licencia

Este proyecto es de uso educativo y libre de uso bajo la [MIT License](LICENSE).
