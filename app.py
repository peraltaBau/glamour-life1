from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import urllib.parse 

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "dev-secret")

# Configuración para subir imágenes
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'avif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Crear directorio para imágenes estáticas
IMAGES_FOLDER = 'static/images'
if not os.path.exists(IMAGES_FOLDER):
    os.makedirs(IMAGES_FOLDER)

# Conexión a MongoDB Atlas
MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://peraltabautistaanalicbtis272_db_user:admin123@glamour.diwxvux.mongodb.net/glamour-life1")

try:
    client = MongoClient(
        MONGO_URI,
        tls=True,
        tlsAllowInvalidCertificates=False,
        serverSelectionTimeoutMS=10000
    )
    db = client['glamour-life1'] 
    print("Conexión segura establecida con MongoDB Atlas")
except Exception as e:
    print("Conexión segura falló, intentando modo escolar...")
    try:
        client = MongoClient(
            MONGO_URI,
            tls=True,
            tlsAllowInvalidCertificates=True,
            serverSelectionTimeoutMS=10000
        )
        db = client.get_default_database()
        print("Conexión establecida con MongoDB Atlas (modo escolar sin SSL)")
    except Exception as e:
        db = None
        print("No se pudo conectar con MongoDB Atlas:", e)

# Colecciones - CORREGIDO: usar verificaciones explícitas con None
users_collection = db.users if db is not None else None
products_collection = db.products if db is not None else None
orders_collection = db.orders if db is not None else None

# Verificar si el archivo es una imagen permitida
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/static/img/<path:filename>')
def serve_images(filename):
    return send_from_directory('static/img', filename)

@app.route('/static/images/<path:filename>')
def serve_product_images(filename):
    return send_from_directory('static/images', filename)

# Datos de productos de ejemplo CON IMÁGENES
sample_products = [
    {
        "name": "Base de Maquillaje Líquida",
        "description": "Base de cobertura media con acabado natural, ideal para todo tipo de piel.",
        "price": 25.99,
        "category": "makeup",
        "image": "base_de_maquillaje.jpg"
    },
    {
        "name": "Paleta de Sombras",
        "description": "Paleta con 12 tonos mates y brillantes para crear looks únicos.",
        "price": 32.50,
        "category": "makeup",
        "image": "paleta_de_sombras.jpg"
    },
    {
        "name": "Labial Líquido Mate",
        "description": "Labial de larga duración con acabado mate y fórmula hidratante.",
        "price": 18.75,
        "category": "makeup",
        "image": "labial_liquido_mate.jpg"
    },
    {
        "name": "Máscara de Pestañas",
        "description": "Máscara que alarga y volumiza las pestañas sin grumos.",
        "price": 15.25,
        "category": "makeup",
        "image": "mascara_de_pestanas.jpg"
    },
    # Cuidado del Cabello
    {
        "name": "Shampoo Nutritivo",
        "description": "Shampoo con aceites naturales para cabello seco y dañado.",
        "price": 12.99,
        "category": "hair",
        "image": "shampoo_nutritivo.jpg"
    },
    {
        "name": "Acondicionador Reparador",
        "description": "Acondicionador que repara puntas abiertas y devuelve el brillo.",
        "price": 14.50,
        "category": "hair",
        "image": "acondicionador_reparador.jpg"
    },
    {
        "name": "Crema para Peinar",
        "description": "Crema que define rizos y controla el frizz sin pesar el cabello.",
        "price": 16.75,
        "category": "hair",
        "image": "crema_para_peinar.jpg"
    },
    {
        "name": "Aceite Capilar",
        "description": "Aceite nutritivo para tratamiento intensivo antes del lavado.",
        "price": 22.25,
        "category": "hair",
        "image": "aceite_capilar.jpg"
    },
    # Cuidado de la Piel
    {
        "name": "Limpiador Facial",
        "description": "Gel limpiador que remueve impurezas sin resecar la piel.",
        "price": 18.99,
        "category": "skincare",
        "image": "limpiador_facial.jpg"
    },
    {
        "name": "Crema Hidratante",
        "description": "Hidratante de textura ligera con protección SPF 30.",
        "price": 28.50,
        "category": "skincare",
        "image": "crema_hidratante.jpg"
    },
    {
        "name": "Serum Vitamina C",
        "description": "Serum antioxidante que ilumina y uniforma el tono de la piel.",
        "price": 35.75,
        "category": "skincare",
        "image": "serum_vitamina_c.jpg"
    },
    {
        "name": "Mascarilla Facial",
        "description": "Mascarilla de arcilla para purificar y minimizar poros.",
        "price": 12.25,
        "category": "skincare",
        "image": "mascarilla_facial.jpg"
    }
]

def crear_imagen_simple(nombre_producto, filename, width=300, height=250):
    """Crea una imagen placeholder simple sin dependencias externas"""
    try:
        # Solo crear archivos de texto como marcadores de posición
        # En producción, deberías tener imágenes reales
        images_dir = 'static/images'
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)
        
        path = os.path.join(images_dir, filename)
        
        # Crear un archivo de texto como placeholder
        with open(path, 'w') as f:
            f.write(f"Placeholder para: {nombre_producto}")
        
        print(f"✅ Marcador creado: {filename}")
        return True
    except Exception as e:
        print(f"❌ Error creando {filename}: {e}")
        return False

def inicializar_imagenes_productos():
    """Crea marcadores para todos los productos de ejemplo"""
    print("🖼️ Inicializando marcadores de productos...")
    
    # Mapeo de nombres de archivo a nombres de producto
    mapeo_nombres = {}
    for product in sample_products:
        mapeo_nombres[product['image']] = product['name']
    
    creadas = 0
    for product in sample_products:
        imagen = product['image']
        if not os.path.exists(os.path.join(IMAGES_FOLDER, imagen)):
            nombre_producto = mapeo_nombres.get(imagen, imagen.replace('.', ' ').title())
            if crear_imagen_simple(nombre_producto, imagen):
                creadas += 1
    
    print(f"📸 Se crearon {creadas} marcadores de imagen")
    return creadas

# Inicializar imágenes antes de poblar la base de datos
inicializar_imagenes_productos()

# Insertar productos si no existen - CORREGIDO
if db is not None and products_collection.count_documents({}) == 0:
    products_collection.insert_many(sample_products)
    print("Base de datos poblada con productos de ejemplo")
elif db is not None:
    print("La base de datos ya contiene productos")

if db is not None:
    print(f"Total de productos: {products_collection.count_documents({})}")
else:
    print("Base de datos no disponible")

# Rutas principales
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        email = request.form.get("email", "").strip()
        telefono = request.form.get("telefono", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        if not nombre or not email or not telefono or not password or not confirm_password:
            flash("Completa todos los campos.", "danger")
            return redirect(url_for("register"))
        
        if password != confirm_password:
            flash("Las contraseñas no coinciden.", "danger")
            return redirect(url_for("register"))

        # CORREGIDO: usar 'is not None' en lugar de verificación booleana
        if db is not None:
            # Verificar si el usuario ya existe
            existing_user = users_collection.find_one({"email": email})
            if existing_user:
                flash("Este correo electrónico ya está registrado.", "danger")
                return redirect(url_for("register"))
            
            # Crear nuevo usuario
            users_collection.insert_one({
                "nombre": nombre,
                "email": email,
                "telefono": telefono,
                "password": password  # En una aplicación real, esto debería estar cifrado
            })
            flash("Registro exitoso. Ya puedes iniciar sesión.", "success")
            return redirect(url_for("login"))
        else:
            flash("Error: Base de datos no conectada.", "danger")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if not email or not password:
            flash("Completa todos los campos.", "danger")
            return redirect(url_for("login"))

        # CORREGIDO: usar 'is not None' en lugar de verificación booleana
        if db is not None:
            user = users_collection.find_one({"email": email, "password": password})
            if user:
                session['user_id'] = str(user['_id'])
                session['user_name'] = user['nombre']
                flash(f"Bienvenido/a {user['nombre']}!", "success")
                return redirect(url_for("products"))
            else:
                flash("Credenciales incorrectas.", "danger")
        else:
            flash("Error: Base de datos no conectada.", "danger")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Has cerrado sesión.", "info")
    return redirect(url_for("index"))

@app.route("/products")
def products():
    category = request.args.get('category', 'all')
    
    # CORREGIDO: usar 'is not None' en lugar de verificación booleana
    if db is not None:
        if category == 'all':
            products_list = list(products_collection.find())
        else:
            products_list = list(products_collection.find({"category": category}))
    else:
        products_list = []
        flash("Error: Base de datos no conectada.", "danger")
    
    return render_template("products.html", products=products_list, category=category)

@app.route("/product/<id>")
def product_detail(id):
    # CORREGIDO: usar 'is None' en lugar de verificación booleana negativa
    if db is None:
        flash("Error: Base de datos no conectada.", "danger")
        return redirect(url_for("products"))
    
    try:
        product = products_collection.find_one({"_id": ObjectId(id)})
        if not product:
            flash("Producto no encontrado.", "warning")
            return redirect(url_for("products"))
        
        return render_template("product_detail.html", product=product)
    except Exception as e:
        flash("ID de producto inválido.", "danger")
        return redirect(url_for("products"))

@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    if 'user_id' not in session:
        flash("Debes iniciar sesión para agregar productos al carrito.", "warning")
        return redirect(url_for("login"))
    
    product_id = request.form.get("product_id")
    quantity = int(request.form.get("quantity", 1))
    
    # CORREGIDO: usar 'is not None' en lugar de verificación booleana
    if db is not None:
        try:
            product = products_collection.find_one({"_id": ObjectId(product_id)})
            if product:
                # Inicializar carrito si no existe
                if 'cart' not in session:
                    session['cart'] = {}
                
                cart = session['cart']
                
                # Agregar o actualizar producto en el carrito
                if product_id in cart:
                    cart[product_id]['quantity'] += quantity
                else:
                    cart[product_id] = {
                        'name': product['name'],
                        'price': float(product['price']),
                        'image': product.get('image', ''),
                        'quantity': quantity
                    }
                
                session['cart'] = cart
                session.modified = True
                flash(f"Producto agregado al carrito.", "success")
            else:
                flash("Producto no encontrado.", "danger")
        except Exception as e:
            flash("Error al agregar producto al carrito.", "danger")
    else:
        flash("Error: Base de datos no conectada.", "danger")
    
    return redirect(request.referrer or url_for("products"))

@app.route("/update_cart", methods=["POST"])
def update_cart():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Usuario no autenticado"})
    
    product_id = request.form.get("product_id")
    quantity = int(request.form.get("quantity", 1))
    
    if 'cart' in session and product_id in session['cart']:
        if quantity <= 0:
            # Eliminar producto si la cantidad es 0 o menos
            del session['cart'][product_id]
        else:
            session['cart'][product_id]['quantity'] = quantity
        
        session.modified = True
        
        # Calcular totales
        cart_total = 0
        for item in session['cart'].values():
            cart_total += item['price'] * item['quantity']
        
        return jsonify({
            "success": True,
            "cart_total": cart_total,
            "cart_count": sum(item['quantity'] for item in session['cart'].values())
        })
    
    return jsonify({"success": False, "message": "Producto no encontrado en el carrito"})

@app.route("/remove_from_cart", methods=["POST"])
def remove_from_cart():
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Usuario no autenticado"})
    
    product_id = request.form.get("product_id")
    
    if 'cart' in session and product_id in session['cart']:
        del session['cart'][product_id]
        session.modified = True
        
        # Calcular totales
        cart_total = 0
        for item in session['cart'].values():
            cart_total += item['price'] * item['quantity']
        
        return jsonify({
            "success": True,
            "cart_total": cart_total,
            "cart_count": sum(item['quantity'] for item in session['cart'].values())
        })
    
    return jsonify({"success": False, "message": "Producto no encontrado en el carrito"})

@app.route("/cart")
def cart():
    if 'user_id' not in session:
        flash("Debes iniciar sesión para ver el carrito.", "warning")
        return redirect(url_for("login"))
    
    cart_items = session.get('cart', {})
    cart_total = 0
    for item in cart_items.values():
        cart_total += item['price'] * item['quantity']
    
    return render_template("cart.html", cart_items=cart_items, cart_total=cart_total)

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if 'user_id' not in session:
        flash("Debes iniciar sesión para realizar una compra.", "warning")
        return redirect(url_for("login"))
    
    if 'cart' not in session or not session['cart']:
        flash("Tu carrito está vacío.", "warning")
        return redirect(url_for("products"))
    
    if request.method == "POST":
        # Procesar el pago (simulado)
        # CORREGIDO: usar 'is not None' en lugar de verificación booleana
        if db is not None:
            # Crear orden
            order_data = {
                "user_id": session['user_id'],
                "items": session['cart'],
                "total": sum(item['price'] * item['quantity'] for item in session['cart'].values()),
                "status": "completed"
            }
            orders_collection.insert_one(order_data)
            
            # Limpiar carrito
            session.pop('cart', None)
            session.modified = True
            
            flash("¡Pago realizado con éxito! Tu pedido está en proceso.", "success")
            return render_template("checkout.html", success=True)
        else:
            flash("Error: Base de datos no conectada.", "danger")
    
    cart_items = session.get('cart', {})
    cart_total = sum(item['price'] * item['quantity'] for item in cart_items.values())
    
    return render_template("checkout.html", cart_items=cart_items, cart_total=cart_total, success=False)

# Panel de administración
@app.route("/admin")
def admin():
    # CORREGIDO: usar 'is None' en lugar de verificación booleana negativa
    if db is None:
        flash("Error: Base de datos no conectada.", "danger")
        return redirect(url_for("index"))
    
    products_list = list(products_collection.find())
    return render_template("admin.html", products=products_list)

@app.route("/admin/add_product", methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        price = float(request.form.get("price", 0))
        category = request.form.get("category", "").strip()
        
        # Manejar la imagen
        image_filename = "default_product.jpg"  # Imagen por defecto
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                # Generar nombre único para evitar colisiones
                filename = secure_filename(file.filename)
                unique_filename = f"{os.path.splitext(filename)[0]}_{ObjectId()}{os.path.splitext(filename)[1]}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                image_filename = unique_filename
                flash("Imagen subida correctamente.", "success")
            elif file and file.filename != '':
                flash("Tipo de archivo no permitido.", "danger")
        
        if db is not None:
            products_collection.insert_one({
                "name": name,
                "description": description,
                "price": price,
                "category": category,
                "image": image_filename
            })
            flash("Producto agregado correctamente.", "success")
            return redirect(url_for("admin"))
        else:
            flash("Error: Base de datos no conectada.", "danger")
    
    return render_template("add_product.html")

# Ruta para servir archivos subidos
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/admin/edit_product/<id>", methods=["GET", "POST"])
def edit_product(id):
    if db is None:
        flash("Error: Base de datos no conectada.", "danger")
        return redirect(url_for("admin"))
    
    try:
        product = products_collection.find_one({"_id": ObjectId(id)})
        if not product:
            flash("Producto no encontrado.", "warning")
            return redirect(url_for("admin"))

        if request.method == "POST":
            name = request.form.get("name", "").strip()
            description = request.form.get("description", "").strip()
            price = float(request.form.get("price", 0))
            category = request.form.get("category", "").strip()
            
            # Mantener la imagen actual a menos que se suba una nueva
            image_filename = product.get('image', 'default_product.jpg')
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename != '' and allowed_file(file.filename):
                    # Eliminar imagen anterior si no es la por defecto
                    if image_filename != 'default_product.jpg':
                        old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
                        if os.path.exists(old_image_path):
                            os.remove(old_image_path)

                    # Guardar nueva imagen
                    filename = secure_filename(file.filename)
                    unique_filename = f"{os.path.splitext(filename)[0]}_{ObjectId()}{os.path.splitext(filename)[1]}"
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    file.save(file_path)
                    image_filename = unique_filename
                    flash("Imagen actualizada correctamente.", "success")

            products_collection.update_one(
                {"_id": ObjectId(id)},
                {"$set": {
                    "name": name,
                    "description": description,
                    "price": price,
                    "category": category,
                    "image": image_filename
                }}
            )
            flash("Producto actualizado correctamente.", "success")
            return redirect(url_for("admin"))

        return render_template("edit_product.html", product=product)
    except Exception as e:
        flash("ID de producto inválido.", "danger")
        return redirect(url_for("admin"))

@app.route("/admin/delete_product/<id>", methods=["POST"])
def delete_product(id):
    # CORREGIDO: usar 'is None' en lugar de verificación booleana negativa
    if db is None:
        flash("Error: Base de datos no conectada.", "danger")
        return redirect(url_for("admin"))
    
    try:
        products_collection.delete_one({"_id": ObjectId(id)})
        flash("Producto eliminado correctamente.", "secondary")
    except Exception as e:
        flash("Error al eliminar producto.", "danger")
    
    return redirect(url_for("admin"))

if __name__ == "__main__":
    # Crear directorio de uploads si no existe
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
