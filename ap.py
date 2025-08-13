# archivo: app.py
from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash
import mysql.connector # Conectar a MySQL
from werkzeug.security import generate_password_hash, check_password_hash

# Importar Flask-WTF para CSRF
from flask_wtf import CSRFProtect

# Importar Flask-Login
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

#importar Flask-Mail
from flask_mail import Mail, Message

#importar flask-Pyotp
from datetime import datetime, timedelta, timezone
import pyotp
import random
import string
import secrets

# Importar Flask-Talisman 
from flask import Flask
from flask_talisman import Talisman

from better_profanity import Profanity

# Inicializar la censura con tu lista personalizada
profanity = Profanity()
profanity.load_censor_words_from_file('palabras_malas.txt')

#importar flask limiter
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.secret_key = 'mi_clave_secreta' # Clave secreta para sesiones, cookies, etc. 

limiter = Limiter(
    app=app,
    key_func=get_remote_address, # Función para obtener la dirección IP del cliente
    default_limits=["200 per day", "60 per hour"] #limita las opciones q no estan limitadas
)

#flask talisman
csp = {
    'default-src': ["'self'"],
    'style-src': ["'self'", "https://cdn.jsdelivr.net", "'unsafe-inline'"],
    'script-src': ["'self'", 'https://cdn.jsdelivr.net', "'unsafe-inline'"],
    'font-src': ["'self'", 'https://fonts.googleapis.com', 'https://fonts.gstatic.com'],
    'frame-ancestors': ["'self'"]
}

# Inicializar Talisman con todas las protecciones
Talisman(
    app,
    force_https=True,                          # Redirige HTTP → HTTPS
    strict_transport_security=True,            # Activa HSTS (solo deja pasar con un link "seguro")
    frame_options='DENY',                      # Bloquea clickjacking
    content_security_policy=csp,               # Aplica tu CSP personalizada
    x_content_type_options='nosniff',          # Evita sniffing de MIME
    referrer_policy='no-referrer'              # Protege datos en enlaces salientes
)
# --- Protección CSRF ---
csrf = CSRFProtect(app)

# --- Configuración de la base de datos (centralizada para evitar repetición) ---
DB_CONFIG = {
    'host': "yamanote.proxy.rlwy.net",
    'port': 33483,
    'user': "root",
    'password': "BNeAADHQCVLNkxkYTyLSjUqSPVxfrWvH",
    'database': "railway"
}

#para censurar con corazones
def censurar_con_corazones(texto):
    censurado = profanity.censor(texto, censor_char='*')
    return censurado.replace('*', '❤')

#-C-O-N-F-I-G-U-R-A-C-I-O-N--M-A-I-L

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='soportes.zettinno.cet@gmail.com',
    MAIL_PASSWORD='tplb flie cpya oxos',
    MAIL_DEFAULT_SENDER=('cet', 'soportes.zettinno.cet@gmail.com')
)
mail = Mail(app)

#------------------------------------

#----F-U-N-C-I-O-N-E-S--P-Y-O-T-P----
#.....despues las podemos usar.......

def generar_otp(intervalo=600):
    secreto = pyotp.random_base32()  
    totp = pyotp.TOTP(secreto, interval=intervalo)
    codigo = totp.now()
    return secreto, codigo

def verificar_otp(secreto, codigo, intervalo=600):
    totp = pyotp.TOTP(secreto, interval=intervalo)
    return totp.verify(codigo)


#------------------------------------

# --- Inicializar Flask-Login ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'iniciarsesion' # Nombre de la función de vista para el login
login_manager.login_message = "Por favor, inicia sesión para acceder a esta página." # Mensaje predeterminado

# --- Clase User para Flask-Login ---
class User(UserMixin):
    def __init__(self, id_usu, nom_usu, email, contraseña_hash, rol):
        self.id = id_usu # Flask-Login espera que el ID se acceda a través de .id
        self.nom_usu = nom_usu
        self.email = email
        self.contraseña_hash = contraseña_hash
        self.rol = rol

    # Método requerido por Flask-Login para obtener el ID unico del usuario
    def get_id(self):
        return str(self.id)

# --- user_loader para Flask-Login ---
# desde el ID de usuario almacenado en la sesion
@login_manager.user_loader
def load_user(user_id):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id_usu, nom_usu, email, contraseña, rol FROM usuario WHERE id_usu = %s", (user_id,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()
        if user_data:
            return User(user_data['id_usu'], user_data['nom_usu'], user_data['email'], user_data['contraseña'], user_data['rol'])
        return None
    except mysql.connector.Error as err:
        print(f"Error al cargar usuario de DB: {err}")
        return None
    

# --- RUTAS DE NAVEGACIÓN GENERAL ---
@app.route('/') #ruta para la página de inicio
def inicio():
    if current_user.is_authenticated:
        return redirect(url_for('indexhomeoinicio'))  # Redirige si ya está logueado
    return render_template('index/indexprincipal.html')  # Si no va al menu principal

@app.route('/comunicatenosotros')
def comnos():
    return render_template('index/indexcentralayuda.html')

#__________________________________
#desde acá empieza el registro
@app.route('/crearcuenta')
def regi():
    # Redirección si el usuario ya está autenticado
    # if current_user.is_authenticated:
    #     flash('Ya has iniciado sesión.', 'info')
    #     return redirect(url_for('inicio'))
    
    if current_user.is_authenticated:
        flash('Ya has iniciado sesión.', 'info')
        return redirect(url_for('inicio'))
    # Si NO verificó el OTP, lo manda a la página de ingresar código
    if not session.get('otp_verificado'):
        flash('Primero debes verificar el código OTP.', 'warning')
        return redirect(url_for('inicio'))  
    return render_template('index/indexcrearcuenta.html')

@app.route('/crearcuenta/registrar', methods=['POST'])
@limiter.limit("10 per hour")
def dataregistro():
    datosdesdejs = request.json
    nombre = censurar_con_corazones(datosdesdejs['name'])
    mail =  session['email_para_verificacion_registro']
    contra = datosdesdejs['contra']
    confcontra = datosdesdejs['confcontra']
    rol='normal'

    if contra != confcontra:
        # CAMBIO: Devolver JSON consistente con otras rutas de API
        return jsonify({"exito": False, "error": "La contraseña y la confirmación no son iguales, intente nuevamente"}), 400

    try:
        conn = mysql.connector.connect(**DB_CONFIG) # Usar DB_CONFIG
        cursor = conn.cursor()

        # Verificar si el email ya existe
        cursor.execute("SELECT id_usu FROM usuario WHERE email = %s", (mail,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            # CAMBIO: Devolver JSON consistente
            return jsonify({"exito": False, "error": "El email ya está registrado."}), 409 # Conflict

        hash_contra = generate_password_hash(contra)
        sql = "INSERT INTO usuario(nom_usu, email, contraseña,rol) VALUES (%s, %s, %s, %s)"
        valores = (nombre, mail, hash_contra, rol)
        cursor.execute(sql, valores)
        conn.commit()
        cursor.close()
        conn.close()
        session.pop('otp_verificado', None)
        # Devolver JSON consistente
        return jsonify({"exito": True, "mensaje": "Usuario registrado correctamente"})
    except Exception as e:
        print(f"Error al registrar el usuario: {e}") # Para depuración
        # Devolver JSON consistente
        return jsonify({"exito": False, "error": f"Error al registrar el usuario: {e}"}), 500

#hasta aca es lo de crear cuenta
#________________________________

#ACA RUTASS PROVISORIAS (2FA)

@app.route("/perfil")
def perfil():
    return render_template('index/indexusuario.html')

@app.route("/actualizar")
def actualizar():
    if not session.get('otp_verificado'):
        flash('Primero debes verificar el codigo que se te a enviado al mail', 'warning')
        return redirect(url_for('inicio'))
    return render_template('index/1ProvisorioActuContra.html')

@app.route("/cambiar")
def Cambiar():
    return render_template('index/1ProvisorioEnviarCorreo.html')

@app.route("/IngresarCodigo")
def otp():
    return render_template('index/1ProvisorioOTP.html')
#-----------------------------------------------
# PROCESO DE CARGAR EL CORREO EN LA BD Y HACER EL CODIGUITO OTP

@app.route('/CambiarContra', methods=['POST'])
@limiter.limit("3 per 5 minutes")
#@limiter.limit("1 per hour")
def cambiar_contra():
    data = request.get_json()
    email = data.get('email')
    
    session.pop('email_del_usuario', None)

    if not email:
        return jsonify({'error': 'Email requerido'}), 400

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuario where email=%s",(email,))
    hay_usuario = cursor.fetchone()

    if not hay_usuario:
        session.pop('email_para_verificacion', None)
        session['email_para_verificacion_registro'] = email
        tipo_otp = 'registro'
        asunto_mail = "R-E-G-I-S-T-R-O--C-E-T"
    else:
        session.pop('email_para_verificacion_registro', None)
        session['email_para_verificacion'] = email
        tipo_otp = 'recuperacion'
        asunto_mail = "R-E-E-S-T-A-B-L-E-C-E-R--C-O-N-T-R-A-S-E-Ñ-A"

    otp = ''.join(secrets.choice(string.digits) for _ in range(6))
    expiracion = datetime.now(timezone.utc) + timedelta(minutes=5)
    
    # --- CORRECCIÓN APLICADA ---
    # Usamos el método DELETE + INSERT para ser consistentes y evitar errores.
    cursor.execute("DELETE FROM codigos_verificacion WHERE email = %s AND tipo = %s", (email, tipo_otp))
    cursor.execute("""
        INSERT INTO codigos_verificacion (email, codigo, tipo, expiracion)
        VALUES (%s, %s, %s, %s)
    """, (email, otp, tipo_otp, expiracion))

    conn.commit()
    conn.close()

    try:
        msg = Message(asunto_mail, sender=app.config['MAIL_USERNAME'], recipients=[email])
        msg.body = f"Tu código de verificacion es: {otp}"
        mail.send(msg)
        return jsonify({'success': True}), 200
    except Exception as e:
        print("Error enviando el correo:", e)
        return jsonify({'error': 'No se pudo enviar el código'}), 500

#------------------------------------------------
@app.route('/verificar_codigo', methods=['POST'])
@limiter.limit("5 per minute")
#@limiter.limit("1 per 15 minutes")
def verificar_codigo():
    data = request.get_json()
    codigo_enviado = data.get('cod')

    if 'email_para_verificacion_registro' in session:
        email = session.get('email_para_verificacion_registro')
        tipo = 'registro'
    elif 'email_del_usuario' in session:
        email = session.get('email_del_usuario')
        tipo = 'login'
    elif 'email_para_verificacion' in session:
        email = session.get('email_para_verificacion')
        tipo = 'recuperacion'
    elif 'email_para_rol_up_code' in session:
        email= session.get('email_para_rol_up_code')
        tipo = 'ascender'
    else:
        return jsonify({'error': 'Sesión inválida o expirada. Por favor, inicia el proceso de nuevo.'}), 400

    if not email or not codigo_enviado:
        return jsonify({'error': 'Faltan datos en la solicitud.'}), 400

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)

    sql_query = "SELECT * FROM codigos_verificacion WHERE email = %s AND tipo = %s AND expiracion > NOW()"
    cursor.execute(sql_query, (email, tipo))
    resultado = cursor.fetchone()

    if not resultado:
        conn.close()
        return jsonify({'error': 'El código es incorrecto o ha expirado.'}), 404
    if codigo_enviado != resultado['codigo']:
        conn.close()
        return jsonify({'error': 'Código incorrecto'}), 401
    cursor.execute("DELETE FROM codigos_verificacion WHERE email = %s AND tipo = %s", (email, tipo))
    conn.commit()
    session['otp_verificado'] = True

    if tipo == 'login':
        contraseña = session.get('contra_del_usuario')
        cursor.execute("SELECT * FROM usuario WHERE email=%s", (email,))
        usuario_data = cursor.fetchone()

        if usuario_data and check_password_hash(usuario_data['contraseña'], contraseña):
            user = User(usuario_data['id_usu'], usuario_data['nom_usu'], usuario_data['email'], usuario_data['contraseña'], usuario_data['rol'])
            login_user(user, remember=True)
            session.pop('email_del_usuario', None)
            session.pop('contra_del_usuario', None)
            session.pop('otp_verificado', None)
            conn.close()
            return jsonify({'exito': True, 'redirigir': 'indexhomeoinicio'})
        else:
            conn.close()
            return jsonify({'error': 'La contraseña guardada es incorrecta.'}), 401

    elif tipo == 'registro':
        session.pop('email_del_usuario', None)
        conn.close()
        return jsonify({'exito': True, 'redirigir': '/crearcuenta'})

    elif tipo == 'recuperacion':
        session['email_para_cambio'] = email
        session.pop('email_del_usuario', None)
        conn.close()
        return jsonify({'exito': True, 'redirigir': '/actualizar'})
    
    elif tipo == 'ascender':
       email_usu = session.get('email_usuario_up')
       conn.close()
       return jsonify({'exito': True, 'redirigir': '/upgradear'})
        
#----------------------------------------------------------------------------
# verificar contraseña NUEVAAAAAA

@app.route('/ActualizarContra', methods=['POST'])
def ActualizarContra():
    data = request.get_json()
    contra=data.get('newpassword')
    confcontra=data.get('newconfirm')
    email = session.get('email_para_cambio')  # Recuperás el email guardado
   
    if not contra or not confcontra:
        return jsonify({"exito": False, "error": "Faltan campos requeridos"}), 400

    if contra != confcontra:
        # CAMBIO: Devolver JSON consistente con otras rutas de API
        return jsonify({"exito": False, "error": "La contraseña y la confirmación no son iguales, intente nuevamente"}), 400

    try:
        conn = mysql.connector.connect(**DB_CONFIG) # Usar DB_CONFIG
        cursor = conn.cursor()
        #hasheo de contraseña xd
        hash_contra = generate_password_hash(contra)
        sql = "UPDATE usuario SET contraseña = %s WHERE email = %s"
        valores = ( hash_contra, email)
        cursor.execute(sql, valores)
        conn.commit()
        session.pop('otp_verificado', None) #para q se borre el "permiso" de la sesion
        # Devolver JSON consistente
        return jsonify({"exito": True, "mensaje": "Actualizaste tu contraseña!!!"})
    except Exception as e:
        print(f"Error al actualizar contraseña: {e}") # Para depuración
        # Devolver JSON consistente
        return jsonify({"exito": False, "error": f"Error al actualizar contraseña: {e}"}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()  
#-------------------------------------------------------
#rutas para las páginas de inicio de sesión
@app.route("/iniciarsesion")
def iniciarsesion():
    if current_user.is_authenticated:
        flash('Ya has iniciado sesión.', 'info')
        return redirect(url_for('inicio')) # Redirige si ya está logueado
    return render_template("index/indexiniciarsesion.html")

# La ruta '/crearcuenta' ya está definida arriba como 'regi()'
# @app.route('/crearcuenta') #ruta para la página de registro #cambiar nombre de la ruta
# def crearcuenta():
#     return render_template('index/indexcrearcuenta.html')

@app.route('/indexhomeoinicio') #ruta para la página de inicio
def indexhomeoinicio():
    if not current_user.is_authenticated:
        return redirect(url_for('iniciarsesion'))  # O a otra vista pública
    return render_template('index/indexhomeoinicio.html') 

#desde aca se elige la modalidad
@app.route('/programacion') #ruta para la página de programación
def indexprogramacion():
    return render_template("index/dprogramacionindex.html")

@app.route('/informatica') #ruta para la página de informática
def indexinformatica():
    return render_template("index/dinformaticaindex.html")
#hasta aca se elige la modalidad

#-A-C-A--E-M-P-I-E-Z-A--I-N-F-O-R-M-A-T-I-C-A--C-U-R-S-O-S
#-------------------------------------------------------

#a partir de aca son las materias de 4to Informatica
#4
@app.route('/informatica/4toinformatica')#el mio es el de nro (4to)
def cuarto4():
    return render_template("index/indexin4to.html")
#-------------------------------------------------------

#a partir de aca son las materias de 5to informatica

#5
@app.route('/informatica/5toinformatica')
def quinto5():
    return render_template("index/indexin5to.html")
#-------------------------------------------------------

#a partir de aca son las materias de 6to informatica

#6
@app.route('/informatica/6toinformatica')#el mio es el de nro (6to)
def sexto6():
    return render_template("index/indexin6to.html")
#-------------------------------------------------------

#a partir de aca son las materias de 7mo informatica
#7
@app.route('/informatica/7moinformatica')#el mio es el de nro (7mo)
def septimo7():
    return render_template("index/indexin7mo.html")


#-A-C-A--T-E-R-M-I-N-A--I-N-F-O-R-M-A-T-I-C-A--C-U-R-S-O-S
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#--------------------------------------------------------
#-A-C-A--E-M-P-I-E-Z-A--P-R-O-G-R-A-M-A-C-I-O-N--C-U-R-S-O-S

#a partir de aca son las materias de 4to programación

#8
@app.route('/programacion/4toprogramacion') #ruta para la página de 4to de programación
def index4toprog():
    return render_template("index/indexdcuarto.html")
#-------------------------------------------------------

#a partir de aca son las materias de 5to programación

#9
@app.route('/programacion/5toprogramacion') #ruta para la página de 5to de programación
def index5toprog():
    return render_template("index/indexdquinto.html")
#-------------------------------------------------------

#a partir de aca son las materias de 6to programación

#10
@app.route('/programacion/6toprogramacion') #ruta para la página de 6to de programación
def index6toprog():
    return render_template("index/indexsexto.html")

#-------------------------------------------------------

#a partir de aca son las materias de 7mo programación

#11
@app.route('/programacion/7moprogramacion') #ruta para la página de 7mo de programación
def index7moprog():
    return render_template("index/indexdseptimo.html")

#--------------------------------------------------------------------------------------------
# --- Cierre de Sesión ---
@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    resp = redirect(url_for('inicio'))
    # Borrar la cookie remember (clave por defecto: remember_token)
    resp.delete_cookie('remember_token')
    return resp

# --- Verificación de OTP ---
@app.route('/otp_login', methods=['POST'])
@limiter.limit("5 per minute")
def otp_login():
    datos = request.get_json()
    email = datos.get('email')
    contraseña = datos.get('password')

    session.pop('email_para_verificacion_registro', None)
    session.pop('email_para_verificacion', None)

    session['email_del_usuario'] = email
    session['contra_del_usuario'] = contraseña

    otp = ''.join(secrets.choice(string.digits) for _ in range(6))
    expiracion = datetime.now(timezone.utc) + timedelta(minutes=5)
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # --- CAMBIO IMPORTANTE ---
        # 1. BORRAMOS cualquier código de 'login' anterior para este email.
        # Esto garantiza que siempre trabajemos con el código más reciente.
        cursor.execute("DELETE FROM codigos_verificacion WHERE email = %s AND tipo = 'login'", (email,))

        # 2. INSERTAMOS el nuevo código generado.
        # Ya no necesitamos ON DUPLICATE KEY UPDATE porque siempre empezamos de cero.
        cursor.execute("""
            INSERT INTO codigos_verificacion (email, codigo, tipo, expiracion)
            VALUES (%s, %s, %s, %s)
        """, (email, otp, 'login', expiracion))

        conn.commit()

        msg = Message("I-N-I-C-I-O--S-E-S-I-O-N--C-E-T",
                sender=app.config['MAIL_USERNAME'],
                recipients=[email])
        msg.body = f"Tu código de verificacion es: {otp}"
        mail.send(msg)
        return jsonify({'success': True}), 200
    except Exception as e:
        print("Error en otp_login:", e)
        return jsonify({'error': 'No se pudo enviar el código'}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
    
 #esto se tiene q hacer dsps...

#_____________________________________________________________________________________
#ACA ABAJO DE MI(? ESTABA LO DE /COMENTARIO/MATERIA/IDMAT Y /COMENTARIO METHOD=POST

@app.route('/comentario/materias/<int:id_mat>')
def comentario_materia(id_mat):
    # CAMBIO: Eliminada la importación y conexión duplicada.
    try:
        conn = mysql.connector.connect(**DB_CONFIG) # Usar DB_CONFIG
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT nom_mat FROM materias WHERE id_mat=%s", (id_mat,))
        materias = cursor.fetchone()
        cursor.close()
        conn.close()
        return render_template('index/ComentariosParaTodos.html', id_mat=id_mat, materias=materias, usuario_rol=current_user.rol)
    except mysql.connector.Error as err:
        print(f"Error al obtener materia: {err}")
        flash("Error al cargar la materia.", 'danger')
        return redirect(url_for('inicio')) # O a una página de error

@app.route('/comentario/materias', methods=['POST'])
@login_required # CAMBIO: Protege la creación de comentarios
@limiter.limit("30 per seccond")
def agregar_comentario():
    # CAMBIO: Eliminada la importación y conexión duplicada.
    data = request.get_json()
    titulo = censurar_con_corazones(data['titulo'])
    cont = censurar_con_corazones(data['comment'])
    id_mat = data.get('id_mat') # Usar .get()

    if not all([titulo, cont, id_mat]):
        return jsonify({"success": False, "error": "Faltan datos para el comentario"}), 400

    # CAMBIO: Obtiene el ID del usuario logueado usando current_user
    id_usu = current_user.id

    try:
        conn = mysql.connector.connect(**DB_CONFIG) # Usar DB_CONFIG
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO preg (titulo, cont, id_mat, id_usu) VALUES (%s, %s, %s, %s)",
            (titulo, cont, id_mat, id_usu)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "mensaje": "Comentario agregado correctamente"}) # CAMBIO: Mensaje JSON
    except mysql.connector.Error as err:
        print(f"Error al agregar comentario: {err}")
        return jsonify({"success": False, "error": f"Error al agregar comentario: {err}"}), 500
    except Exception as e: # CAMBIO: Añadir manejo de excepción general
        print(f"Error inesperado al agregar comentario: {e}")
        return jsonify({"success": False, "error": f"Error inesperado: {e}"}), 500

#________________________________________________________________________________________________
#ACA ARRIBA DE MI(? ESTABA LO DE /COMENTARIO/MATERIA/IDMAT Y /COMENTARIO METHOD=POST
@app.route('/get_comentario')
def get_comentario():
    # CAMBIO: Eliminada la importación y conexión duplicada.
    id_mat = request.args.get('id_mat')
    id_usu = current_user.id
    if not id_mat: # CAMBIO: Validación si no se pasa id_mat
        return jsonify({"success": False, "error": "ID de materia requerido"}), 400

    try:
        conn = mysql.connector.connect(**DB_CONFIG) # Usar DB_CONFIG
        # CAMBIO: Simplificado el if/else redundante.
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.id_post, p.titulo, p.cont, p.fecha, u.nom_usu AS usuario, p.id_usu, p.cont_likes,
            EXISTS(
                 SELECT 1 FROM likes_comentarios l
                 WHERE l.id_post = p.id_post AND l.id_usu = %s
               )AS likeado_por_usuario
            FROM preg p
            LEFT JOIN usuario u ON p.id_usu = u.id_usu
            WHERE p.id_mat=%s
            ORDER BY p.fecha DESC
        """, (id_usu, id_mat)) 
        comentarios = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(comentarios)
    except mysql.connector.Error as err:
        print(f"Error al obtener comentarios: {err}")
        return jsonify({"success": False, "error": f"Error al obtener comentarios: {err}"}), 500
    except Exception as e: # CAMBIO: Añadir manejo de excepción general
        print(f"Error inesperado al obtener comentarios: {e}")
        return jsonify({"success": False, "error": f"Error inesperado: {e}"}), 500


@app.route('/responder', methods=['POST'])
@login_required # CAMBIO: Protege la capacidad de responder
@limiter.limit(" 2 per  10 seconds ")
def responder():
    # CAMBIO: Eliminada la importación y conexión duplicada.
    data = request.get_json()
    id_post = data.get('id_post') # Usar .get()
    cont = censurar_con_corazones(data.get('respuesta')) # Usar .get()

    if not all([id_post, cont]):
        return jsonify({"success": False, "error": "Faltan datos para la respuesta"}), 400

    # CAMBIO: Obtiene el ID del usuario logueado usando current_user
    id_usu = current_user.id

    try:
        conn = mysql.connector.connect(**DB_CONFIG) # Usar DB_CONFIG
        cursor = conn.cursor()
        query = "INSERT INTO rta (id_post, id_usu, cont) VALUES (%s, %s, %s)"
        cursor.execute(query, (id_post, id_usu, cont))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True, "mensaje": "Respuesta agregada correctamente"}) # CAMBIO: Mensaje JSON
    except mysql.connector.Error as err:
        print(f"Error al responder: {err}")
        return jsonify({"success": False, "error": f"Error al responder: {err}"}), 500
    except Exception as e: # CAMBIO: Añadir manejo de excepción general
        print(f"Error inesperado al responder: {e}")
        return jsonify({"success": False, "error": f"Error inesperado: {e}"}), 500


@app.route('/get_respuestas/<int:id_post>')
def get_respuestas(id_post):
    try:
        conn = mysql.connector.connect(**DB_CONFIG) # Usar DB_CONFIG
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT r.id_com, r.cont, u.nom_usu AS usuario, r.id_usu,
            (SELECT COUNT(*) FROM likes_rta lr WHERE lr.id_com = r.id_com) AS cont_likes,
            EXISTS(
                SELECT 1 FROM likes_rta lr2
                WHERE lr2.id_com = r.id_com AND lr2.id_usu = %s
            ) AS likeado_por_usuario
        FROM rta r
        LEFT JOIN usuario u ON r.id_usu = u.id_usu
        WHERE r.id_post = %s
        ORDER BY r.id_com ASC
        """, (current_user.id, id_post))
        respuestas = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(respuestas)
    except mysql.connector.Error as err:
        print(f"Error al obtener respuestas: {err}")
        return jsonify({"success": False, "error": f"Error al obtener respuestas: {err}"}), 500
    except Exception as e: # CAMBIO: Añadir manejo de excepción general
        print(f"Error inesperado al obtener respuestas: {e}")
        return jsonify({"success": False, "error": f"Error inesperado: {e}"}), 500

#---RUTA PARA DAR LIKE A UN COMENTARIO---
@app.route('/api/like', methods=['POST'])
@login_required
@limiter.limit("100 per hour")
def like_comment():
    data = request.get_json()
    print("Datos recibidos en /api/like:", data)
    comment_id = data.get('comment_id')
    id_usu_like = current_user.id
    if not comment_id:
        return jsonify({'success': False, 'error': 'Falta comment_id'}), 400
    if not id_usu_like:
        return jsonify({'success': False, 'error': 'Falta id_usu_like'}), 2323

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # # Sumar un like
        # cursor.execute("UPDATE preg SET cont_likes = IFNULL(cont_likes, 0) + 1 WHERE id_post = %s", (comment_id,))
        # conn.commit()
        # Paso 1: verificar si ya existe el like
        cursor.execute("SELECT * FROM likes_comentarios WHERE id_post = %s AND id_usu = %s", (comment_id, id_usu_like))
        existe = cursor.fetchone()
        if existe:
         # Ya había dado like → quitarlo
            cursor.execute("UPDATE preg SET cont_likes = cont_likes - 1 WHERE id_post = %s", (comment_id,))
            cursor.execute("DELETE FROM likes_comentarios WHERE id_post = %s AND id_usu = %s", (comment_id, id_usu_like))
        else:
        # No había dado like → agregarlo
            cursor.execute("UPDATE preg SET cont_likes = IFNULL(cont_likes, 0) + 1 WHERE id_post = %s", (comment_id,))
            cursor.execute("INSERT INTO likes_comentarios (id_post, id_usu) VALUES (%s, %s)", (comment_id, id_usu_like))

        conn.commit()
        # Obtener el total actualizado
        cursor.execute("SELECT cont_likes FROM preg WHERE id_post = %s", (comment_id,))
        total = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'total': total})
    except Exception as e:
        print("Error en like_comment:", e)
        return jsonify({'success': False, 'error': str(e)}), 500

#---RUTA PARA DAR LIKE A UNA RESPUESTA---
@app.route('/api/like_respuesta', methods=['POST'])
@login_required
@limiter.limit("100 per hour")
def like_rta():
    data = request.get_json()
    id_com = data.get('id_com')
    id_usu = current_user.id
    if not id_usu:
        return jsonify({'success': False, 'error': 'No autorizado'}), 401

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM likes_rta WHERE id_com=%s AND id_usu=%s", (id_com, id_usu))
    liked = cursor.fetchone()
    if liked:
        # Sacar like
        cursor.execute("DELETE FROM likes_rta WHERE id_com=%s AND id_usu=%s", (id_com, id_usu))
        conn.commit()
        liked_now = False
    else:
        # Agregar like
        cursor.execute("INSERT INTO likes_rta (id_com, id_usu) VALUES (%s, %s)", (id_com, id_usu))
        conn.commit()
        liked_now = True
    # Contar likes totales
    cursor.execute("SELECT COUNT(*) FROM likes_rta WHERE id_com=%s", (id_com,))
    total = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return jsonify({'total': total, 'liked': liked_now})

#---RUTA PARA ELIMINAR COMENTARIOS---
@app.route('/eliminar_comentario', methods=['POST'])
@login_required
def eliminar_comentario():
    data = request.get_json()
    if not data or 'id_post' not in data:
        return jsonify({'success': False, 'error': 'Datos inválidos'}), 400

    id_post = data['id_post']
    id_usu = current_user.id
    rol_usuario = current_user.rol

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Obtener las respuestas asociadas a la pregunta
        cursor.execute("SELECT id_com FROM rta WHERE id_post = %s", (id_post,))
        respuestas = cursor.fetchall()
        id_rtas = [row[0] for row in respuestas]

        # Borrar los likes de esas respuestas (si hay)
        if id_rtas:
            placeholders = ','.join(['%s'] * len(id_rtas))
            cursor.execute(f"DELETE FROM likes_rta WHERE id_com IN ({placeholders})", tuple(id_rtas))

        # Borrar las respuestas asociadas a la pregunta (si hay)
        cursor.execute("DELETE FROM rta WHERE id_post = %s", (id_post,))

        # Borrar los likes de la pregunta (si hay)
        cursor.execute("DELETE FROM likes_comentarios WHERE id_post = %s", (id_post,))

        if rol_usuario == 'admin':
            cursor.execute("DELETE FROM preg WHERE id_post = %s", (id_post,))
        else:
        # Borrar la pregunta, pero solo si pertenece al usuario actual
            cursor.execute("DELETE FROM preg WHERE id_post = %s AND id_usu = %s", (id_post, id_usu))
        borrados = cursor.rowcount

        if borrados == 0:
            conn.rollback()
            return jsonify({'success': False, 'error': 'No sos dueño del comentario'}), 403

        conn.commit()
        return jsonify({'success': True})

    except Exception as e:
        print("Error al eliminar comentario:", e)
        return jsonify({'success': False, 'error': 'Error interno al eliminar comentario'}), 500

    finally:
        cursor.close()
        conn.close()




#---RUTA PARA ELIMINAR RESPUESTAS---
@app.route('/eliminar_respuesta', methods=['POST'])
@login_required
def eliminar_respuesta():
    import mysql.connector
    data = request.get_json()
    id_com = data['id_com']
    id_usu = current_user.id
    rol_usuario = current_user.rol
    if not id_usu:
        return jsonify({'success': False, 'error': 'No autorizado'}), 401
    conn = mysql.connector.connect(
        host="yamanote.proxy.rlwy.net",
        port=33483,
        user="root",
        password="BNeAADHQCVLNkxkYTyLSjUqSPVxfrWvH",
        database="railway"
    )
    cursor = conn.cursor()
    cursor.execute("DELETE FROM likes_rta WHERE id_com=%s",(id_com,))
    if (rol_usuario=='admin'):
        cursor.execute("DELETE FROM rta WHERE id_com=%s", (id_com,))
    else:
        cursor.execute("DELETE FROM rta WHERE id_com=%s AND id_usu=%s", (id_com, id_usu))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'success': True})


#ACA PANEL ADMIIIIIIIIIIN 

@app.route("/paneladmin")
def paneladmin():
    return render_template("index/paneladmin.html")



@app.route('/api/users', methods=['GET', 'POST'])
def get_users():
    conn = mysql.connector.connect(**DB_CONFIG)
    if not conn:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    cursor = conn.cursor(dictionary=True) # Usamos dictionary=True para obtener un diccionario por cada fila
    query = "SELECT id_usu, nom_usu,email,rol FROM usuario"
    
    try:
        cursor.execute(query)
        users = cursor.fetchall() # Obtiene todas las filas como una lista de diccionarios
    except mysql.connector.Error as err:
        print(f"Error en la consulta: {err}")
        users = []
    finally:
        cursor.close()
        conn.close()

    return jsonify(users)

@app.route('/upgradear', methods=['POST'])
def ascender():
    id_usuario = session.get('id_usuario_up')
    rol_usuario = session.get('rol_usuario_up')

    
    if not id_usuario or not rol_usuario:
        return jsonify({'success': False, 'error': 'No mandaste usuario'}), 401
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # pasa de NORMAL ========> MODERADOR
        if rol_usuario == 'normal':
            cursor.execute("UPDATE usuario SET rol='moderador' WHERE id_usu=%s", (id_usuario,))
            conn.commit()
            return jsonify({'success': True}), 200

        # pasa de MODERADOR ============> ADMINISTRADOR
        elif rol_usuario == 'moderador':
            cursor.execute("UPDATE usuario SET rol='admin' WHERE id_usu=%s", (id_usuario,))
            conn.commit()
            return jsonify({'success': True}), 200

        else:
            return jsonify({'success': False, 'error': f"Rol inválido: {rol_usuario}"}), 400

    except Exception as e:
        print(f"❌ Error al upgradear usuario {id_usuario}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass




@app.route('/eliminar_usuario', methods=['POST'])
def eliminarusuario():
    datos_js = request.get_json()
    id_usuario = datos_js.get('id_usuario')

    if not id_usuario:
        return jsonify({'success': False, 'error': 'No mandaste usuario'}), 401

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # 0. Eliminar likes hechos por el usuario en comentarios
        cursor.execute("DELETE FROM likes_comentarios WHERE id_usu = %s", (id_usuario,))

        # 1. Eliminar likes de TODAS las respuestas que serán eliminadas
        cursor.execute("""
            DELETE FROM likes_rta 
            WHERE id_com IN (
                SELECT id_com FROM rta 
                WHERE id_usu = %s OR id_post IN (
                    SELECT id_post FROM preg WHERE id_usu = %s
                )
            )
        """, (id_usuario, id_usuario))

        # 2. Eliminar respuestas a preguntas del usuario
        cursor.execute("""
            DELETE FROM rta 
            WHERE id_post IN (
                SELECT id_post FROM preg WHERE id_usu = %s
            )
        """, (id_usuario,))

        # 3. Eliminar likes de preguntas del usuario
        cursor.execute("""
            DELETE FROM likes_comentarios 
            WHERE id_post IN (
                SELECT id_post FROM preg WHERE id_usu = %s
            )
        """, (id_usuario,))

        # 4. Eliminar preguntas del usuario
        cursor.execute("DELETE FROM preg WHERE id_usu = %s", (id_usuario,))

        # 5. Eliminar respuestas propias del usuario
        cursor.execute("DELETE FROM rta WHERE id_usu = %s", (id_usuario,))

        # 6. Finalmente, eliminar el usuario
        cursor.execute("DELETE FROM usuario WHERE id_usu = %s", (id_usuario,))
        conn.commit()

        return jsonify({'success': True}), 200

    except Exception as e:
        print(f"❌ Error al eliminar usuario {id_usuario}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass


@app.route('/down',methods=['POST'])
def down():
    data = request.get_json()
    id_usuario= data.get('id_usuario')
    rol_usuario=data.get('rol_usuario')
    if not id_usuario:
        return jsonify({'success': False, 'error': 'No mandaste usuario'}), 401

    if rol_usuario == 'admin':
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("update usuario set rol='moderador' where id_usu=%s",(id_usuario,))
            conn.commit()
        except Exception as e:
            print(f"❌ Error al degradar usuario {id_usuario}: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    elif rol_usuario == 'moderador':
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("update usuario set rol='normal' where id_usu=%s",(id_usuario,))
            conn.commit()
        except Exception as e:
            print(f"❌ Error al degradar usuario {id_usuario}: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    else:
        print(f"❌ Error no hay rol apto para degradar {id_usuario}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

#RUTAS DE ROLES OSEA DE LOS CODIGOS Q MANDAN CNDO QUERES CAMBIAR EL ROL DE ALGUIEN

@app.route('/otp_roles', methods=['POST'])
@limiter.limit("5 per minute")
def cambiar_roles_ascender():
    datos = request.get_json() #aca pide q rol es desde js con un json (hacer dssp)
    if not datos:
        return jsonify({'error': 'No se recibió JSON válido'}), 400

    email_mail = 'foro.cet4@gmail.com'
    rol_usuario = datos.get('rol_usuario')
    email= datos.get('mail_usuario') #cambie esas 2 lineas pq decian cosas q el js no mandaba xd

    session.pop('email_para_verificacion_registro', None)
    session.pop('email_para_verificacion', None)

    session['id_usuario_up'] = datos.get('id_usuario')
    session['rol_usuario_up'] = datos.get('rol_usuario')
    session['email_para_rol_up_code'] = email_mail #rol_up pq sube el rango/rol tiene q ser el mail de cet4 pq la verga esa dsps se manda al /veificar codigo y el codigo se manda a cet4 entonces va a verificar cet4
    session['rol'] = rol_usuario
    session['email_usuario_up'] = email

    otp = ''.join(secrets.choice(string.digits) for _ in range(6))
    expiracion = datetime.now(timezone.utc) + timedelta(minutes=5)
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # --- CAMBIO IMPORTANTE ---
        # 1. BORRAMOS cualquier código de 'ascender' anterior para este email.
        # Esto garantiza que siempre trabajemos con el código más reciente.
        cursor.execute("DELETE FROM codigos_verificacion WHERE email = %s AND tipo = 'ascender'", (email_mail,))

        # 2. INSERTAMOS el nuevo código generado.
        # Ya no necesitamos ON DUPLICATE KEY UPDATE porque siempre empezamos de cero.
        cursor.execute("""
            INSERT INTO codigos_verificacion (email, codigo, tipo, expiracion)
            VALUES (%s, %s, %s, %s)
        """, (email_mail, otp, 'ascender', expiracion))

        conn.commit()

        msg = Message("PETICION-DE-ASCENSION DE USUARIO",
                sender=app.config['MAIL_USERNAME'],
                recipients=[email_mail])
        msg.body = f"Tu código de verificacion es: {otp}"
        mail.send(msg)
        return jsonify({'success': True}), 200
    except Exception as e:
        print("Error en otp_login:", e)
        return jsonify({'error': 'No se pudo enviar el código'}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()



if __name__ == "__main__":
    print("iniciando flask..")
    app.run(debug=True)
