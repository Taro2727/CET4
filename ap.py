# archivo: app.py
from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash,abort
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

#importar para notificaciones
from pywebpush import webpush, WebPushException
import json
from flask import send_from_directory

#para hacer funciones herramientosas (functools)
from functools import wraps

# # from cryptography.hazmat.primitives.asymmetric import ec
# # from cryptography.hazmat.primitives import serialization
# # import base64

# # # Generar clave EC P-256
# # private_key = ec.generate_private_key(ec.SECP256R1())
# # public_key = private_key.public_key()

# # # Clave privada en formato Base64 URL Safe (para el servidor)
# # priv_bytes = private_key.private_numbers().private_value.to_bytes(32, 'big')
# # VAPID_PRIVATE_KEY = base64.urlsafe_b64encode(priv_bytes).decode('utf-8').rstrip('=')

# # # Clave pública en formato Base64 URL Safe (para el navegador)
# # pub_bytes = public_key.public_bytes(
# #     encoding=serialization.Encoding.X962,
# #     format=serialization.PublicFormat.UncompressedPoint
# # )
# VAPID_PUBLIC_KEY = base64.urlsafe_b64encode(pub_bytes).decode('utf-8').rstrip('=')

# Claims
VAPID_CLAIMS = {
    "sub": "mailto:soportes.zettinno.cet@gmail.com"
}

# print("✅ VAPID_PUBLIC_KEY:", VAPID_PUBLIC_KEY)
# print("✅ VAPID_PRIVATE_KEY:", VAPID_PRIVATE_KEY)


app = Flask(__name__)
app.secret_key = 'mi_clave_secreta' # Clave secreta para sesiones, cookies, etc. 

#configuracion pra notificaciones push
VAPID_PUBLIC_KEY = """BPFRnskk36NpTs6rraQ9KZqwlK-7gmK3Dne6dt-khKt-Q-93tdgNwKc5SI3cDYxGUNyw4vJpMONIMV1Ws4m14zg"""

VAPID_PRIVATE_KEY = """h40P9y69H-8sEGrsL-t94fC89vG2x5qryJas6nU1A7I"""

VAPID_CLAIMS = {
    "sub": "mailto:soportes.zettinno.cet@gmail.com"
}

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
    'host': "crossover.proxy.rlwy.net",
    'port': 51139,
    'user': "root",
    'password': "pZjJhZfsMwsGFNWJBPqDazxYveDQEZMY",
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


def check_ban(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT id_ban, fecha_fin 
                    FROM Baneo 
                    WHERE id_usu = %s AND activo = TRUE
                """, (current_user.id,))
                ban = cursor.fetchone()

                if ban:
                    hoy = datetime.now()
                    if hoy < ban['fecha_fin']:
                        # Baneo ==> activo
                        cursor.close()
                        conn.close()
                        logout_user()
                        return render_template("index/baneado.html")
                    else:
                        # Baneo vencido ==> borrar
                        cursor.execute('DELETE FROM Baneo WHERE id_usu = %s', (current_user.id,))
                        conn.commit()

                cursor.close()
                conn.close()
            except Exception as e:
                print("Error al verificar baneo:", e)
        return f(*args, **kwargs)
    return decorated_function

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
#funcion reutilizable para enviar notificaciones push
def notif_push(subscription_info, message_body, id_usu=None):
    VAPID_CLAIMS = {"sub": "mailto:soportes.zettinno.cet@gmail.com"}
    """
    Función para enviar una notificación push.
    """
    try:
        webpush(
            subscription_info=subscription_info,
            data=json.dumps(message_body),  # <-- CORREGIDO
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims=VAPID_CLAIMS
        )
        print("Notificación enviada con éxito.")
    except WebPushException as ex:
        print("❌ Error al enviar notificación:", ex)
        # Si la suscripción ha expirado o no es válida (código 410 Gone),
        # es una buena práctica eliminarla de la base de datos.
        if ex.response and ex.response.status_code == 410:
            print("Suscripción expirada. Se recomienda eliminarla.")
        # No relanzamos el error para no detener el flujo si falla una sola notificación
    except Exception as e:
        print("❌ Error inesperado en notif_push:", e)
#------------------------------------

# --- Inicializar Flask-Login ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'iniciarsesion' # Nombre de la función de vista para el login
login_manager.login_message = "Por favor, inicia sesión para acceder a esta página." # Mensaje predeterminado

# --- Clase User para Flask-Login ---
class User(UserMixin):
    def __init__(self, id_usu, nom_usu, email, contraseña_hash, rol,avatar):
        self.id = id_usu # Flask-Login espera que el ID se acceda a través de .id
        self.nom_usu = nom_usu
        self.email = email
        self.contraseña_hash = contraseña_hash
        self.rol = rol
        self.avatar = avatar

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
        cursor.execute("SELECT id_usu, nom_usu, email, contraseña, rol, avatar FROM usuario WHERE id_usu = %s", (user_id,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()
        if user_data:
            return User(user_data['id_usu'], user_data['nom_usu'], user_data['email'], user_data['contraseña'], user_data['rol'],user_data['avatar'])
        return None
    except mysql.connector.Error as err:
        print(f"Error al cargar usuario de DB: {err}")
        return None
    

# --- RUTAS DE NAVEGACIÓN GENERAL ---
@app.route('/sw.js') #ruta de notificaciones push
def service_worker():
    return send_from_directory('.', 'sw.js', mimetype='application/javascript')

@app.route('/') #ruta para la página de inicio
@check_ban 
def inicio():
    if current_user.is_authenticated:
        return redirect(url_for('indexhomeoinicio'))  # Redirige si ya está logueado
    return render_template('index/indexprincipal.html')  # Si no va al menu principal

@app.route('/comunicatenosotros')
def comnos():
    return render_template('index/centroayuda.html')

#__________________________________
#desde acá empieza el registro
@app.route('/crearcuenta')
def regi():
    # Redirección si el usuario ya está autenticado
    # if current_user.is_authenticated:
    #     return redirect(url_for('inicio'))
    
    if current_user.is_authenticated:
        return redirect(url_for('inicio'))
    # Si NO verificó el OTP, lo manda a la página de ingresar código
    if not session.get('otp_verificado'):
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
#rutas de notificaciones push
@app.route('/vapid_key_publica', methods=['GET'])
@login_required
def vapid_key_publica():
    return jsonify({'public_key': VAPID_PUBLIC_KEY})

@app.route('/guardarsuscripcion', methods=['POST'])
@login_required
def guardar_suscripcion():
    suscripcion_data = request.json
    if not suscripcion_data:
        return jsonify({'success': False, 'error': 'No se recibieron datos de suscripción'}), 400

    id_usu = current_user.id
    suscripcion_json = json.dumps(suscripcion_data)

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        # Evitar duplicados: Borrar suscripciones viejas del mismo usuario antes de insertar la nueva
        cursor.execute("DELETE FROM suscripcion_push WHERE id_usu = %s", (id_usu,))
        cursor.execute(
            "INSERT INTO suscripcion_push (id_usu, suscripcion_json) VALUES (%s, %s)",
            (id_usu, suscripcion_json)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except mysql.connector.Error as err:
        print(f"Error al guardar suscripción: {err}")
        return jsonify({'success': False, 'error': 'Error de base de datos'}), 500
    
def guardar_notificacion(id_usu, tipo, mensaje):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO notificaciones (id_usu, tipo, mensaje)
            VALUES (%s, %s, %s)
        """, (id_usu, tipo, mensaje))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Error al guardar notificación:", e)

@app.route('/panelnotificaciones')
@login_required
@check_ban
def panelnotificaciones():
    return render_template('index/panelnotificaciones.html')


@app.route('/mis_notificaciones_data')
@login_required
def mis_notificaciones_data():
    """Ruta que devuelve las notificaciones del usuario en formato JSON, con opción de ordenarlas."""
    try:
        # Obtenemos el criterio de orden desde la URL (ej: /mis_notificaciones_data?orden=antiguo)
        orden = request.args.get('orden', 'reciente')
        
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        id_usu = current_user.id

        # Creamos la consulta SQL base
        query_base = "SELECT id_notif, tipo, mensaje, fecha, leida FROM notificaciones WHERE id_usu = %s"

        # Añadimos el orden a la consulta según el parámetro recibido
        if orden == 'antiguo':
            query_final = query_base + " ORDER BY fecha ASC"
        else: # Por defecto y para 'reciente'
            query_final = query_base + " ORDER BY fecha DESC"
        
        cursor.execute(query_final, (id_usu,))
        notificaciones = cursor.fetchall()
        
        # Marcamos las notificaciones como leídas (si hay alguna)
        if notificaciones:
            # Creamos una lista solo con los IDs de las notificaciones no leídas
            notif_ids_no_leidas = [n['id_notif'] for n in notificaciones if not n['leida']]
            
            if notif_ids_no_leidas:
                # Usamos un formato seguro para la consulta IN (...)
                placeholders = ','.join(['%s'] * len(notif_ids_no_leidas))
                update_query = f"UPDATE notificaciones SET leida = TRUE WHERE id_notif IN ({placeholders})"
                cursor.execute(update_query, tuple(notif_ids_no_leidas))
                conn.commit()

        cursor.close()
        conn.close()

        return jsonify({'success': True, 'notificaciones': notificaciones})

    except mysql.connector.Error as err:
        print(f"Error al obtener notificaciones: {err}")
        return jsonify({'success': False, 'error': 'Error de base de datos'}), 500
    except Exception as e:
        print(f"Error inesperado en mis_notificaciones_data: {e}")
        return jsonify({'success': False, 'error': 'Error inesperado'}), 500
    
@app.route('/eliminar_notificacion/<int:notif_id>', methods=['DELETE'])
@login_required
def eliminar_notificacion(notif_id):
    try:
        id_usu = current_user.id
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Asegurarse de que el usuario es el dueño de la notificación
        cursor.execute("SELECT id_notif FROM notificaciones WHERE id_notif = %s AND id_usu = %s", (notif_id, id_usu))
        notificacion = cursor.fetchone()

        if not notificacion:
            return jsonify({"success": False, "error": "Notificación no encontrada o no pertenece al usuario"}), 404

        # Eliminar la notificación de la base de datos
        cursor.execute("DELETE FROM notificaciones WHERE id_notif = %s", (notif_id,))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "Notificación eliminada correctamente"}), 200

    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": f"Error de base de datos: {err}"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": f"Error inesperado: {e}"}), 500
    
def notif_email(destinatario, asunto, cuerpo):
    try:
        # Verificar preferencia antes de enviar
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT notif_email FROM usuario WHERE email = %s", (destinatario,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if not row or not row['notif_email']:
            print("📧 Usuario con email", destinatario, "tiene desactivadas las notificaciones por correo.")
            return  # No enviar

        msg = Message(
            subject=asunto,
            sender=app.config['MAIL_USERNAME'],
            recipients=[destinatario],
            body=cuerpo
        )
        mail.send(msg)
        print("📧 Email enviado a", destinatario)
    except Exception as e:
        print("❌ Error al enviar email de notificación:", e)

@app.route('/eliminar-suscripcion', methods=['POST'])
def eliminar_suscripcion():
    data = request.get_json(silent=True) or {}
    # Espera al menos el endpoint de la suscripción
    endpoint = data.get('endpoint')
    if not endpoint:
        return jsonify({'success': False, 'error': 'Falta endpoint de suscripción'}), 400
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        # Buscamos y eliminamos la suscripción que contenga ese endpoint
        # El uso de JSON_EXTRACT es más preciso, pero LIKE funciona si la estructura es consistente.
        # Esta consulta busca el endpoint dentro del JSON almacenado como texto.
        cursor.execute(
            "DELETE FROM suscripcion_push WHERE id_usu = %s AND suscripcion_json LIKE %s",
            (current_user.id, f'%"{endpoint}"%')
        )
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Suscripción eliminada para el endpoint: {endpoint}")
        return jsonify({'success': True})
    except mysql.connector.Error as err:
        print(f"Error al eliminar suscripción: {err}")
        return jsonify({'success': False, 'error': 'Error de base de datos'}), 500

# ruta para la tuerca barra lateral
@app.route('/configuracion')
@login_required
@check_ban
def configuracion():
    return render_template('index/tuercabarralateral.html')

@app.route('/guardar-configuracion', methods=['POST'])
@login_required
@check_ban
def guardar_configuracion():
    """
    Inicia el flujo de cambio de contraseña desde Configuración.
    """
    # Limpia sesiones viejas para evitar conflictos
    session.pop('email_para_verificacion', None)
    session.pop('email_para_verificacion_registro', None)
    session.pop('email_del_usuario', None)

    pass_actual = request.form.get('pass_actual')
    pass_nueva = request.form.get('pass_nueva')
    pass_confirmar = request.form.get('pass_confirmar')

    if not all([pass_actual, pass_nueva, pass_confirmar]):
        return redirect(url_for('configuracion'))

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT contraseña FROM usuario WHERE id_usu = %s", (current_user.id,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()

        if not user_data or not check_password_hash(user_data['contraseña'], pass_actual):
            return redirect(url_for('configuracion'))
    except Exception as e:
        return redirect(url_for('configuracion'))

    if pass_nueva != pass_confirmar:
        return redirect(url_for('configuracion'))

    try:
        email_usuario = current_user.email
        tipo_otp = 7 
        
        otp = ''.join(secrets.choice(string.digits) for _ in range(6))
        expiracion = datetime.now(timezone.utc) + timedelta(minutes=5)
        
        conn_otp = mysql.connector.connect(**DB_CONFIG)
        cursor_otp = conn_otp.cursor()
        
        cursor_otp.execute("DELETE FROM codigos_verificacion WHERE email = %s AND tipo = %s", (email_usuario, tipo_otp))
        cursor_otp.execute("""
            INSERT INTO codigos_verificacion (email, codigo, tipo, expiracion)
            VALUES (%s, %s, %s, %s)
        """, (email_usuario, otp, tipo_otp, expiracion))
        conn_otp.commit()
        cursor_otp.close()
        conn_otp.close()

        msg = Message("C-A-M-B-I-O--C-O-N-T-R-A-S-E-Ñ-A--C-O-N-F-I-G-U-R-A-C-I-O-N", 
                      sender=app.config['MAIL_USERNAME'], 
                      recipients=[email_usuario])
        msg.body = f"Tu código de verificacion es: {otp}"
        mail.send(msg)
        
        session['email_para_configuracion'] = email_usuario
        session['nueva_pass_hasheada_config'] = generate_password_hash(pass_nueva, method='pbkdf2:sha256')
        
        return redirect(url_for('otp'))
        
    except Exception as e:
        return redirect(url_for('configuracion'))

@app.route('/toggle-email-notifications', methods=['POST'])
@login_required
def toggle_email_notifications():
    data = request.get_json()
    enable = data.get('enable')

    if enable is None:
        return jsonify({'success': False, 'error': 'Falta el estado enable'}), 400

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Guardar preferencia en la tabla usuario
        cursor.execute("UPDATE usuario SET notif_email = %s WHERE id_usu = %s", (enable, current_user.id))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'success': True})
    except mysql.connector.Error as err:
        print(f"Error al actualizar notificaciones email: {err}")
        return jsonify({'success': False, 'error': 'Error de base de datos'}), 500
    
@app.route('/toggle-push-notifications', methods=['POST'])
@login_required
def toggle_push_notifications():
    data = request.get_json()
    enable = data.get('enable')

    if enable is None:
        return jsonify({'success': False, 'error': 'Falta el estado enable'}), 400

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("UPDATE usuario SET notif_push = %s WHERE id_usu = %s", (enable, current_user.id))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except mysql.connector.Error as err:
        print(f"Error al actualizar notificaciones push: {err}")
        return jsonify({'success': False, 'error': 'Error de base de datos'}), 500
    
@app.route('/mis-preferencias-notif', methods=['GET'])
@login_required
def mis_preferencias_notif():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT notif_email, notif_push FROM usuario WHERE id_usu = %s", (current_user.id,))
        prefs = cursor.fetchone()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'prefs': prefs})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/test_notificacion') #ruta para probar si las notificaciones funcionan
@login_required
def test_notificacion():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT suscripcion_json FROM suscripcion_push WHERE id_usu = %s", (current_user.id,))
        subs = cursor.fetchall()
        for sub in subs:
            suscripcion_info_json = sub[0]
            print("Datos de suscripción leídos de la DB:", suscripcion_info_json) # <--- Agrega esta línea
            try:
                notif_push(json.loads(suscripcion_info_json), {
                    "title": "🚀 Notificación de prueba",
                    "body": "¡Hola! Esto es solo un test para verificar que todo funciona."
                })
            except Exception as e:
                print(f"Error: Datos de suscripción en la DB no son JSON válidos para el usuario {current_user.id}")
    except Exception as e:
        print(f"Error en la ruta de prueba: {e}")
        # AQUI AGREGAMOS LA RESPUESTA DE ERROR QUE FALTABA
        return jsonify({"success": False, "error": str(e)})


#ACA RUTASS PROVISORIAS (2FA)

@app.route("/perfil")
def perfil():
    return render_template('index/indexusuario.html')

@app.route("/actualizar")
def actualizar():
    if not session.get('otp_verificado'):
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
        tipo_otp = 3
        asunto_mail = "R-E-G-I-S-T-R-O--C-E-T"
    else:
        session.pop('email_para_verificacion_registro', None)
        session['email_para_verificacion'] = email
        tipo_otp = 1
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
def verificar_codigo():
    data = request.get_json()
    codigo_enviado = data.get('cod')

    if 'email_para_configuracion' in session:
        email = session.get('email_para_configuracion')
        tipo = 7 #config
    elif 'email_para_rol_up_code' in session:
        email = session.get('email_para_rol_up_code')
        tipo = 4 #ascender
    elif 'email_para_rol_down_code' in session:
        email = session.get('email_para_rol_down_code')
        tipo = 5 #degradar
    elif 'email_para_eliminar_code' in session:
        email = session.get('email_para_eliminar_code')
        tipo = 6 #eliminar
    elif 'email_para_verificacion_registro' in session:
        email = session.get('email_para_verificacion_registro')
        tipo = 3 #registro
    elif 'email_del_usuario' in session:
        email = session.get('email_del_usuario')
        tipo = 2 #login
    elif 'email_para_verificacion' in session:
        email = session.get('email_para_verificacion')
        tipo = 1 #recuperacion
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

    # --- Lógica de redirección después de la verificación ---
    if tipo == 2:
        contraseña = session.get('contra_del_usuario')
        cursor.execute("SELECT * FROM usuario WHERE email=%s", (email,))
        usuario_data = cursor.fetchone()

        if usuario_data and check_password_hash(usuario_data['contraseña'], contraseña):
            user = User(usuario_data['id_usu'], usuario_data['nom_usu'], usuario_data['email'], usuario_data['contraseña'], usuario_data['rol'],usuario_data['avatar'])
            login_user(user, remember=True)
            session.pop('email_del_usuario', None)
            session.pop('contra_del_usuario', None)
            session.pop('otp_verificado', None)
            conn.close()
            return jsonify({'exito': True, 'redirigir': 'indexhomeoinicio'})
        else:
            conn.close()
            return jsonify({'error': 'La contraseña guardada es incorrecta.'}), 401

    elif tipo == 3:
        session.pop('email_del_usuario', None)
        conn.close()
        return jsonify({'exito': True, 'redirigir': '/crearcuenta'})

    elif tipo == 1:
        session['email_para_cambio'] = email
        session.pop('email_del_usuario', None)
        conn.close()
        return jsonify({'exito': True, 'redirigir': '/actualizar'})
    
    elif tipo == 7:
        try:
            nueva_pass_hasheada = session['nueva_pass_hasheada_config']
            id_usuario_actual = current_user.id # Guardamos el ID antes de hacer logout
            
            conn_update = mysql.connector.connect(**DB_CONFIG)
            cursor_update = conn_update.cursor()
            cursor_update.execute("UPDATE usuario SET contraseña = %s WHERE email = %s", (nueva_pass_hasheada, email))
            conn_update.commit()
            cursor_update.close()
            conn_update.close()
            
            # --- SOLUCIÓN DE SEGURIDAD PARA EL BUG DE LA SESIÓN ---
            usuario_actualizado = load_user(id_usuario_actual)
            logout_user()
            login_user(usuario_actualizado)
            # --- FIN DE LA SOLUCIÓN ---
            
            session.pop('email_para_configuracion', None)
            session.pop('nueva_pass_hasheada_config', None)
            session.pop('otp_verificado', None)
            
            conn.close() 
            return jsonify({'exito': True, 'redirigir': '/configuracion'})
        except Exception as e:
            conn.close()
            return jsonify({'error': f'No se pudo actualizar la contraseña: {e}'}), 500

    elif tipo == 4:
       email_usu = session.get('email_usuario_up')
       conn.close()
       return jsonify({'exito': True, 'redirigir': '/upgradear'})
    
    elif tipo == 5:
        email_usu= session.get('email_usuario_down')
        conn.close()
        return jsonify({'exito': True, 'redirigir': '/down'})
    
    elif tipo == 6:
        conn.close()
        return jsonify({'exito': True, 'redirigir': '/eliminar_usuario'})
    
    # Si algún tipo no tiene un manejo explícito
    conn.close()
    return jsonify({'error': 'Tipo de operación no manejada.'}), 500
        
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
        return redirect(url_for('inicio')) # Redirige si ya está logueado
    return render_template("index/indexiniciarsesion.html")

# La ruta '/crearcuenta' ya está definida arriba como 'regi()'
# @app.route('/crearcuenta') #ruta para la página de registro #cambiar nombre de la ruta
# def crearcuenta():
#     return render_template('index/indexcrearcuenta.html')

@app.route('/indexhomeoinicio')
@check_ban 
def indexhomeoinicio():
    if not current_user.is_authenticated and not session.get('guest'):
        return redirect(url_for('iniciarsesion'))
    return render_template('index/indexhomeoinicio.html') 

@app.route('/entrar_como_invitado')
def entrar_como_invitado():
    session['guest'] = True
    return redirect(url_for('indexhomeoinicio'))

#desde aca se elige la modalidad
@app.route('/programacion') #ruta para la página de programación
@check_ban
def indexprogramacion():
    return render_template("index/dprogramacionindex.html")

@app.route('/informatica') #ruta para la página de informática
@check_ban
def indexinformatica():
    return render_template("index/dinformaticaindex.html")
#hasta aca se elige la modalidad

#-A-C-A--E-M-P-I-E-Z-A--I-N-F-O-R-M-A-T-I-C-A--C-U-R-S-O-S
#-------------------------------------------------------

#a partir de aca son las materias de 4to Informatica
#4
@app.route('/informatica/4toinformatica')#el mio es el de nro (4to)
@check_ban
def cuarto4():
    return render_template("index/indexin4to.html")
#-------------------------------------------------------

#a partir de aca son las materias de 5to informatica

#5
@app.route('/informatica/5toinformatica')
@check_ban
def quinto5():
    return render_template("index/indexin5to.html")
#-------------------------------------------------------

#a partir de aca son las materias de 6to informatica

#6
@app.route('/informatica/6toinformatica')#el mio es el de nro (6to)
@check_ban
def sexto6():
    return render_template("index/indexin6to.html")
#-------------------------------------------------------

#a partir de aca son las materias de 7mo informatica
#7
@app.route('/informatica/7moinformatica')#el mio es el de nro (7mo)
@check_ban
def septimo7():
    return render_template("index/indexin7mo.html")


#-A-C-A--T-E-R-M-I-N-A--I-N-F-O-R-M-A-T-I-C-A--C-U-R-S-O-S
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#--------------------------------------------------------
#-A-C-A--E-M-P-I-E-Z-A--P-R-O-G-R-A-M-A-C-I-O-N--C-U-R-S-O-S

#a partir de aca son las materias de 4to programación

#8
@app.route('/programacion/4toprogramacion') #ruta para la página de 4to de programación
@check_ban
def index4toprog():
    return render_template("index/indexdcuarto.html")
#-------------------------------------------------------

#a partir de aca son las materias de 5to programación

#9
@app.route('/programacion/5toprogramacion') #ruta para la página de 5to de programación
@check_ban
def index5toprog():
    return render_template("index/indexdquinto.html")
#-------------------------------------------------------

#a partir de aca son las materias de 6to programación

#10
@app.route('/programacion/6toprogramacion') #ruta para la página de 6to de programación
@check_ban
def index6toprog():
    return render_template("index/indexsexto.html")

#-------------------------------------------------------

#a partir de aca son las materias de 7mo programación

#11
@app.route('/programacion/7moprogramacion') #ruta para la página de 7mo de programación
@check_ban
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
# En ap.py

@app.route('/otp_login', methods=['POST'])
@limiter.limit("5 per minute")
def otp_login():
    datos = request.get_json()
    email = datos.get('email')
    contraseña = datos.get('password')

    if not email or not contraseña:
        return jsonify({'error': 'Email y contraseña son requeridos.'}), 400

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        # --- INICIO DE LA CORRECCIÓN DE SEGURIDAD ---
        # 1. Buscamos al usuario en la base de datos PRIMERO.
        cursor.execute("SELECT * FROM usuario WHERE email = %s", (email,))
        usuario_data = cursor.fetchone()

        # 2. Verificamos si el usuario existe Y si la contraseña es correcta.
        if not usuario_data or not check_password_hash(usuario_data['contraseña'], contraseña):
            cursor.close()
            conn.close()
            # Devolvemos un error genérico para no dar pistas a atacantes.
            return jsonify({'error': 'Email o contraseña incorrectos.'}), 401
        
        # --- FIN DE LA CORRECCIÓN ---

        # Si llegamos hasta acá, significa que la contraseña es CORRECTA.
        # Ahora sí, procedemos a enviar el OTP.
        
        session.pop('email_para_verificacion_registro', None)
        session.pop('email_para_verificacion', None)
        session['email_del_usuario'] = email
        session['contra_del_usuario'] = contraseña

        otp = ''.join(secrets.choice(string.digits) for _ in range(6))
        expiracion = datetime.now(timezone.utc) + timedelta(minutes=5)
        
        cursor.execute("DELETE FROM codigos_verificacion WHERE email = %s AND tipo =2", (email,))
        cursor.execute("""
            INSERT INTO codigos_verificacion (email, codigo, tipo, expiracion)
            VALUES (%s, %s, %s, %s)
        """, (email, otp, 2, expiracion))
        conn.commit()

        msg = Message("I-N-I-C-I-O--S-E-S-I-O-N--C-E-T",
                      sender=app.config['MAIL_USERNAME'],
                      recipients=[email])
        msg.body = f"Tu código de verificacion es: {otp}"
        mail.send(msg)
        
        return jsonify({'success': True}), 200

    except Exception as e:
        print("Error en otp_login:", e)
        return jsonify({'error': 'Ocurrió un error en el servidor.'}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
    
 #esto se tiene q hacer dsps...

#_____________________________________________________________________________________
#ACA ABAJO DE MI(? ESTABA LO DE /COMENTARIO/MATERIA/IDMAT Y /COMENTARIO METHOD=POST

@app.route('/comentario/materias/<int:id_mat>')
@check_ban
def comentario_materia(id_mat):
    # CAMBIO: Eliminada la importación y conexión duplicada.
    try:
        conn = mysql.connector.connect(**DB_CONFIG) # Usar DB_CONFIG
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT nom_mat FROM materias WHERE id_mat=%s", (id_mat,))
        materias = cursor.fetchone()
        cursor.close()
        conn.close()

        usuario_rol=current_user.rol if current_user.is_authenticated else None #para obtener el rol
        return render_template('index/ComentariosParaTodos.html', id_mat=id_mat, materias=materias, usuario_rol=usuario_rol, is_authenticated=current_user.is_authenticated )
    except mysql.connector.Error as err:
        print(f"Error al obtener materia: {err}")
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
    orden = request.args.get('orden', 'reciente')
    
    if not id_mat: # CAMBIO: Validación si no se pasa id_mat
        return jsonify({"success": False, "error": "ID de materia requerido"}), 400

    try:
        conn = mysql.connector.connect(**DB_CONFIG) # Usar DB_CONFIG
        # CAMBIO: Simplificado el if/else redundante.
        cursor = conn.cursor(dictionary=True)
        if current_user.is_authenticated:
            query_likeado="EXISTS(SELECT 1 FROM likes_comentarios WHERE id_post = p.id_post AND id_usu = %s) AS likeado_por_usuario"
            params = (current_user.id, id_mat)
        else:
            query_likeado = "FALSE AS likeado_por_usuario"
            params = (id_mat,)
        query = f"""
            SELECT p.id_post, p.titulo, p.cont,p.id_usu, u.nom_usu AS usuario, p.fecha, 
                   COUNT(l.id_like) AS cont_likes,
                   {query_likeado}
            FROM preg p
            LEFT JOIN usuario u ON p.id_usu = u.id_usu
            LEFT JOIN likes_comentarios l ON p.id_post = l.id_post
            WHERE p.id_mat = %s
            GROUP BY p.id_post, p.titulo, p.cont,p.id_usu, u.nom_usu, p.fecha
        """

        # Agregar ORDER BY basado en 'orden'
        if orden == 'reciente':
            query += " ORDER BY p.fecha DESC"
        elif orden == 'antiguo':
            query += " ORDER BY p.fecha ASC"
        elif orden == 'mas-likes':
            query += " ORDER BY cont_likes DESC, p.fecha DESC"  # Tiebreaker por fecha
        elif orden == 'menos-likes':
            query += " ORDER BY cont_likes ASC, p.fecha DESC"  # Tiebreaker por fecha
        else:
            query += " ORDER BY p.fecha DESC"  # Default
        cursor.execute(query, params)
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
@login_required
@limiter.limit(" 2 per  10 seconds ")
def responder():
    data = request.get_json()
    id_post = data.get('id_post')
    cont = censurar_con_corazones(data.get('respuesta'))

    if not all([id_post, cont]):
        return jsonify({"success": False, "error": "Faltan datos para la respuesta"}), 400

    id_usu = current_user.id

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # 1. Obtenemos el ID del autor de la pregunta original
        cursor.execute("SELECT id_usu FROM preg WHERE id_post = %s", (id_post,))
        post_author_data = cursor.fetchone()
        id_autor_post = post_author_data['id_usu'] if post_author_data else None

        # 2. Insertamos la nueva respuesta en la base de datos
        cursor.execute("INSERT INTO rta (id_post, id_usu, cont) VALUES (%s, %s, %s)", (id_post, id_usu, cont))
        conn.commit() # Guardamos la respuesta antes de notificar

        # 3. Lógica de Notificación 
        if id_autor_post and id_autor_post != id_usu:
            
            # --- INICIO DE LA CORRECCIÓN ---
            # Verificamos las preferencias de notificación del autor ANTES de enviar nada
            cursor.execute("SELECT notif_push, notif_email, email FROM usuario WHERE id_usu = %s", (id_autor_post,))
            prefs = cursor.fetchone()

            if prefs:
                # Enviar Notificación PUSH (si están activadas)
                if prefs['notif_push']:
                    cursor.execute("SELECT suscripcion_json FROM suscripcion_push WHERE id_usu = %s", (id_autor_post,))
                    subscriptions = cursor.fetchall()
                    for sub in subscriptions:
                        notif_payload = {
                            "title": "💬 ¡Nueva Respuesta!",
                            "body": f"{current_user.nom_usu} ha respondido a tu pregunta."
                        }
                        suscripcion_dict = json.loads(sub['suscripcion_json'])
                        notif_push(suscripcion_dict, notif_payload)
                
                # Enviar Notificación por EMAIL (si están activadas)
                if prefs['notif_email'] and prefs['email']:
                    notif_email(
                        destinatario=prefs['email'],
                        asunto="💬 Nueva respuesta en tu post",
                        cuerpo=f"{current_user.nom_usu} respondió a tu pregunta en el foro CET."
                    )

            # Guardamos la notificación en la base de datos (esto siempre se hace)
            guardar_notificacion(id_autor_post, 1, f"{current_user.nom_usu} respondió tu pregunta.")

        cursor.close()
        conn.close()
        return jsonify({"success": True, "mensaje": "Respuesta agregada correctamente"})
        
    except Exception as e:
        print(f"Error inesperado al responder: {e}")
        return jsonify({"success": False, "error": f"Error inesperado: {e}"}), 500

@app.route('/get_respuestas/<int:id_post>')
def get_respuestas(id_post):
    try:
        conn = mysql.connector.connect(**DB_CONFIG) # Usar DB_CONFIG
        cursor = conn.cursor(dictionary=True)
        if current_user.is_authenticated:
            query_likeado = "EXISTS(SELECT 1 FROM likes_rta WHERE id_com = r.id_com AND id_usu = %s) AS likeado_por_usuario"
            params = (current_user.id, id_post)
        else:
            query_likeado = "FALSE AS likeado_por_usuario"
            params = (id_post,)
        cursor.execute(f"""
            SELECT r.id_com, r.cont, u.nom_usu AS usuario, r.id_usu,
            (SELECT COUNT(*) FROM likes_rta lr WHERE lr.id_com = r.id_com) AS cont_likes,
            {query_likeado}
            FROM rta r
            LEFT JOIN usuario u ON r.id_usu = u.id_usu
            WHERE r.id_post = %s
            ORDER BY r.id_com ASC
        """, params)
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
        cursor = conn.cursor(dictionary=True)

        # # Sumar un like
        # cursor.execute("UPDATE preg SET cont_likes = IFNULL(cont_likes, 0) + 1 WHERE id_post = %s", (comment_id,))
        # conn.commit()
        # Paso 1: verificar si ya existe el like
        cursor.execute("SELECT id_usu FROM preg WHERE id_post = %s ", (comment_id,))
        autor_data=cursor.fetchone()
        id_autor_data= autor_data['id_usu'] if autor_data else None

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

            if id_autor_data and id_autor_data != id_usu_like:
                cursor.execute("SELECT suscripcion_json FROM suscripcion_push WHERE id_usu = %s", (id_autor_data,))
                suscripcion = cursor.fetchall()
                for sub in suscripcion:
                    notif ={
                        "title": "Nuevo like en tu comentario",
                        "body": f"{current_user.nom_usu} ha dado like a tu comentario",
                    }
                    suscripcion_dict = json.loads(sub['suscripcion_json'])
                    notif_push(suscripcion_dict, notif) # <-- CORREGIDO
                    guardar_notificacion(id_autor_data, 1, f"{current_user.nom_usu} dio like a tu comentario.")
                    cursor.execute("SELECT email FROM usuario WHERE id_usu = %s", (id_autor_data,))
                    email_data = cursor.fetchone()
                    if email_data:
                        notif_email(
                            destinatario=email_data['email'],
                            asunto="👍 Nuevo like en tu comentario",
                            cuerpo=f"{current_user.nom_usu} dio like a tu comentario en el foro CET."
    )

        conn.commit()
        # Obtener el total actualizado
        cursor.execute("SELECT cont_likes FROM preg WHERE id_post = %s", (comment_id,))
        total = cursor.fetchone()["cont_likes"] #lo cambie antes estaba asi [0] por si no funciona 
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
    cursor.execute("SELECT id_usu FROM preg WHERE id_post = %s", (id_com,))
    post_author_data = cursor.fetchone()
    id_autor_post = post_author_data['id_usu'] if post_author_data else None

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
        if id_autor_post and id_autor_post != id_usu:
                # 4. Buscar la suscripción del autor
                cursor.execute("SELECT suscripcion_json FROM suscripcion_push WHERE id_usu = %s", (id_autor_post,))
                subscriptions = cursor.fetchall()
                for sub in subscriptions:
                    # 5. Enviar la notificación
                    notificacion_payload = {
                        "title": "👍 ¡Nuevo Like!",
                        "body": f"{current_user.nom_usu} le ha dado like a tu pregunta."
                    }
                    suscripcion_dict = json.loads(sub['suscripcion_json'])
                    notif_push(suscripcion_dict, notificacion_payload) # <-- CORREGIDO
                    guardar_notificacion(id_autor_post, 1, f"{current_user.nom_usu} dio like a tu comentario.")
                    cursor.execute("SELECT email FROM usuario WHERE id_usu = %s", (id_autor_post,))
                    email_data = cursor.fetchone()
                    if email_data:
                        notif_email(
                            destinatario=email_data['email'],
                            asunto="👍 Nuevo like en tu comentario",
                            cuerpo=f"{current_user.nom_usu} dio like a tu comentario en el foro CET."
                        )
        conn.commit()
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
    data = request.get_json(silent=True) or {}
    id_com = data.get('id_com')
    if not id_com:
        return jsonify({'success': False, 'error': 'id_com missing'}), 400

    id_usu = current_user.id
    rol_usuario = getattr(current_user, 'rol', None)

    try:
        conn = mysql.connector.connect(**DB_CONFIG, connection_timeout=10)
        cursor = conn.cursor()

        # verificar existencia y autor de la respuesta
        cursor.execute("SELECT id_usu FROM rta WHERE id_com = %s", (id_com,))
        row = cursor.fetchone()
        if not row:
            return jsonify({'success': False, 'error': 'Respuesta no encontrada'}), 404
        autor_id = row[0]

        # eliminar según permisos
        if rol_usuario == 'admin':
            cursor.execute("DELETE FROM rta WHERE id_com = %s", (id_com,))
        else:
            cursor.execute("DELETE FROM rta WHERE id_com = %s AND id_usu = %s", (id_com, id_usu))

        if cursor.rowcount == 0:
            conn.rollback()
            return jsonify({'success': False, 'error': 'No autorizado o ya eliminado'}), 403

        # borrar likes asociados
        cursor.execute("DELETE FROM likes_rta WHERE id_com = %s", (id_com,))
        conn.commit()
        return jsonify({'success': True})
    except mysql.connector.Error as err:
        print('DB error eliminar_respuesta:', err)
        return jsonify({'success': False, 'error': 'db', 'detail': str(err)}), 500
    except Exception as e:
        print('Error eliminar_respuesta:', e)
        return jsonify({'success': False, 'error': 'server', 'detail': str(e)}), 500
    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass


#ACA PANEL ADMIIIIIIIIIIN 

@app.route("/paneladmin")
@check_ban
@login_required
def paneladmin():
    return render_template("index/paneladmin.html")



# app.py

@app.route('/api/users', methods=['GET', 'POST'])
def get_users():
    conn = mysql.connector.connect(**DB_CONFIG)
    if not conn:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    cursor = conn.cursor(dictionary=True)

    try:
        # Consulta SQL corregida para usar el nombre de tabla 'Baneo'
        cursor.execute("""
            SELECT
                u.id_usu, u.nom_usu, u.email, u.rol,
                b.id_ban IS NOT NULL AS baneado
            FROM usuario u
            LEFT JOIN Baneo b ON u.id_usu = b.id_usu
        """)
        users = cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error en la consulta: {err}")
        users = []
    finally:
        cursor.close()
        conn.close()

    return jsonify(users)
# @app.route('/api/bans', methods=['GET', 'POST'])
# def get_bans():
#     conn = mysql.connector.connect(**DB_CONFIG)
#     if not conn:
#         return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

#     cursor = conn.cursor(dictionary=True) # Usamos dictionary=True para obtener un diccionario por cada fila
#     query = "SELECT id_ban,id_usu,activo FROM baneo"
    
#     try:
#         cursor.execute(query)
#         users = cursor.fetchall() # Obtiene todas las filas como una lista de diccionarios
#     except mysql.connector.Error as err:
#         print(f"Error en la consulta: {err}")
#         users = []
#     finally:
#         cursor.close()
#         conn.close()

#     return jsonify(users)


# --- Nueva ruta para verificar el estado de baneo ---
# @app.route('/api/ban_status/<int:id_user>', methods=['GET'])
# @login_required
# def get_ban_status():

#     # Asegúrate de que solo un administrador pueda usar esta ruta
#     if current_user.rol != 'admin':  #  es el rol de admin en tu código
#         return jsonify({"error": "Acceso denegado"}), 403

#     try:
#         conn = mysql.connector.connect(**DB_CONFIG)
#         cursor = conn.cursor(dictionary=True)

#         # Consulta si hay un baneo activo para el usuario
#         query = "SELECT activo FROM Baneo WHERE id_usu = %s AND activo = TRUE"
#         cursor.execute(query, (id_usuario,))
#         ban_status = cursor.fetchone()

#         cursor.close()
#         conn.close()

#         # Si ban_status no es None, significa que hay un baneo activo
#         is_banned = ban_status is not None
        
#         return jsonify({"is_banned": is_banned})

#     except mysql.connector.Error as err:
#         print(f"Error al obtener el estado de baneo: {err}")
#         return jsonify({"error": "Error de base de datos"}), 500

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
    id_usuario = session.get('id_usuario_eliminar')

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


@app.route('/down', methods=['POST'])
def down():
    # El 'data' del request no se usa en este caso, ya que los datos vienen de la sesión.
    # Es seguro mantener la línea, pero no es funcionalmente necesaria para esta lógica.
   
    id_usuario = session.get('id_usuario_down')
    rol_usuario = session.get('rol_usuario_down')

    # Si no hay ID de usuario en la sesión, la petición no es válida.
    if not id_usuario:
        return jsonify({'success': False, 'error': 'No se encontró el usuario en la sesión'}), 401

    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        if rol_usuario == 'admin':
            cursor.execute("UPDATE usuario SET rol='moderador' WHERE id_usu=%s", (id_usuario,))
            conn.commit()
            # ¡AÑADIDO! Si todo salió bien, devolvemos un éxito.
            return jsonify({'success': True, 'message': 'Usuario degradado a moderador.'}), 200
            
        elif rol_usuario == 'moderador':
            cursor.execute("UPDATE usuario SET rol='normal' WHERE id_usu=%s", (id_usuario,))
            conn.commit()
            # ¡AÑADIDO! Si todo salió bien, devolvemos un éxito.
            return jsonify({'success': True, 'message': 'Usuario degradado a normal.'}), 200

        else:
            # Si el rol no es admin ni moderador, no se puede degradar.
            print(f"❌ Error: Rol '{rol_usuario}' no apto para degradar para el usuario {id_usuario}")
            return jsonify({'success': False, 'error': 'El rol del usuario no puede ser degradado.'}), 400

    except Exception as e:
        # Si ocurre un error en la base de datos, lo capturamos y devolvemos el error.
        print(f"❌ Error al degradar usuario {id_usuario}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
        
    finally:
        # Esto es crucial: asegura que la conexión se cierre siempre.
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

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
        cursor.execute("DELETE FROM codigos_verificacion WHERE email = %s AND tipo = 4", (email_mail,))

        # 2. INSERTAMOS el nuevo código generado.
        # Ya no necesitamos ON DUPLICATE KEY UPDATE porque siempre empezamos de cero.
        cursor.execute("""
            INSERT INTO codigos_verificacion (email, codigo, tipo, expiracion)
            VALUES (%s, %s, %s, %s)
        """, (email_mail, otp, 4, expiracion))

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


@app.route('/otp_down', methods=['POST'])
@limiter.limit("5 per minute")
def cambiar_roles_down():
    datos = request.get_json() #aca pide q rol es desde js con un json (hacer dssp)
    if not datos:
        return jsonify({'error': 'No se recibió JSON válido'}), 400

    email_mail = 'foro.cet4@gmail.com'
    rol_usuario = datos.get('rol_usuario')
    email= datos.get('mail_usuario') #cambie esas 2 lineas pq decian cosas q el js no mandaba xd

    session.pop('email_para_verificacion_registro', None)
    session.pop('email_para_verificacion', None)

    session['id_usuario_down'] = datos.get('id_usuario')
    session['rol_usuario_down'] = datos.get('rol_usuario')
    session['email_para_rol_down_code'] = email_mail #rol_up pq sube el rango/rol tiene q ser el mail de cet4 pq la verga esa dsps se manda al /veificar codigo y el codigo se manda a cet4 entonces va a verificar cet4
    session['rol'] = rol_usuario
    session['email_usuario_up'] = email

    otp = ''.join(secrets.choice(string.digits) for _ in range(6))
    expiracion = datetime.now(timezone.utc) + timedelta(minutes=5)
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # --- CAMBIO IMPORTANTE ---
        # 1. BORRAMOS cualquier código de 'degradar' anterior para este email.
        # Esto garantiza que siempre trabajemos con el código más reciente.
        cursor.execute("DELETE FROM codigos_verificacion WHERE email = %s AND tipo = 5", (email_mail,))

        # 2. INSERTAMOS el nuevo código generado.
        # Ya no necesitamos ON DUPLICATE KEY UPDATE porque siempre empezamos de cero.
        cursor.execute("""
            INSERT INTO codigos_verificacion (email, codigo, tipo, expiracion)
            VALUES (%s, %s, %s, %s)
        """, (email_mail, otp, 5, expiracion))

        conn.commit()

        msg = Message("PETICION-DE-DEGRADACIÓN-DE-USUARIO",
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

@app.route('/otp_eliminar', methods=['POST'])
@limiter.limit("5 per minute")
def otp_eliminar():
    datos = request.get_json() #aca pide q rol es desde js con un json (hacer dssp)
    if not datos:
        return jsonify({'error': 'No se recibió JSON válido'}), 400

    email_mail = 'foro.cet4@gmail.com'
    rol_usuario = datos.get('rol_usuario') #<--- nose si sirve ahr
    email= datos.get('mail_usuario') # <-------- esa no sirve xq "eliminar_usuario" no trabaja con mail, sino con id_usu

    session.pop('email_para_verificacion_registro', None)
    session.pop('email_para_verificacion', None)

    session['id_usuario_eliminar'] = datos.get('id_usuario')
    session['rol_usuario_eliminar'] = datos.get('rol_usuario')  #<--- nose si sirve ahr
    session['email_para_eliminar_code'] = email_mail #rol_up pq sube el rango/rol tiene q ser el mail de cet4 pq la verga esa dsps se manda al /veificar codigo y el codigo se manda a cet4 entonces va a verificar cet4
    session['email_usuario_eliminar'] = email  #<--- nose si sirve ahr

    session['rol'] = rol_usuario  #<--- nose si sirve ahr
    

    otp = ''.join(secrets.choice(string.digits) for _ in range(6))
    expiracion = datetime.now(timezone.utc) + timedelta(minutes=5)
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # --- CAMBIO IMPORTANTE ---
        # 1. BORRAMOS cualquier código de 'degradar' anterior para este email.
        # Esto garantiza que siempre trabajemos con el código más reciente.
        cursor.execute("DELETE FROM codigos_verificacion WHERE email = %s AND tipo = 6", (email_mail,))

        # 2. INSERTAMOS el nuevo código generado.
        # Ya no necesitamos ON DUPLICATE KEY UPDATE porque siempre empezamos de cero.
        cursor.execute("""
            INSERT INTO codigos_verificacion (email, codigo, tipo, expiracion)
            VALUES (%s, %s, %s, %s)
        """, (email_mail, otp, 6, expiracion))

        conn.commit()

        msg = Message("PETICION-DE-ELIMINACION-DE-USUARIO",
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
@app.route('/ban',methods=['POST'])
def ban():
    data = request.get_json()
    id_usuario= data.get('id_usuario')
    inicio_str= data.get('fecha_inicio')#primero esta en string (str)
    fin_str= data.get('fecha_fin')#primero esta en string (str)
    motivo=data.get('motivo')
    if not data:
        return jsonify({'error': 'No me llego el id del usuario del js panel (linea 1565)'}),400

    if not all([id_usuario, inicio_str, fin_str, motivo]):
        return jsonify({'error': 'Faltan datos.'}), 400
    
    print(f"Fecha de inicio recibida: {inicio_str}")
    print(f"Fecha de fin recibida: {fin_str}")

    try:
        # 1. Convierte las cadenas de texto a objetos datetime
        fecha_inicio = datetime.strptime(inicio_str, '%Y-%m-%d')
        fecha_fin = datetime.strptime(fin_str, '%Y-%m-%d')

        if fecha_inicio > fecha_fin:
            return jsonify({'error': 'La fecha de fin debe ser posterior a la de inicio.'}), 400

        # 2. Realiza la resta entre los objetos datetime
        duracion_delta = fecha_fin - fecha_inicio #Delta es el datetaim ahr de python

        # 3. Obtén la duración en días (un número entero)
        duracion_dias = duracion_delta.days

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Baneo(id_usu, fecha_inicio ,duracion_dias ,motivo ,fecha_fin ,activo) VALUES (%s,%s,%s,%s,%s,%s)',(id_usuario,fecha_inicio,duracion_dias,motivo,fecha_fin,1))
        conn.commit()
        cursor.close()
        conn.close()

        #  Respuesta correcta en caso de éxito
        return jsonify({'exito': True, 'mensaje': 'Usuario baneado correctamente.'}), 200
    except ValueError:
        # Este except captura el error si el formato de fecha es incorrecto
        return jsonify({'error': 'Formato de fecha no válido. Use YYYY-MM-DD.'}), 400
    
    except mysql.connector.Error as err:
        # Este except captura errores de la base de datos
        print(f"Error de MySQL: {err}")
        if conn:
            conn.rollback()
        return jsonify({'error': f'Error en la base de datos: {err}'}), 500
    
    except Exception as e:
        # Este except captura cualquier otro error inesperado
        print(f"Ocurrió un error inesperado: {e}")
        if conn:
            conn.rollback()
        return jsonify({'error': 'Ocurrió un error interno del servidor.'}), 500
    
    finally:
        # Este bloque se ejecuta SIEMPRE, ya sea que haya un error o no
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

@app.route('/unban', methods=['POST'])
def unban():
    data = request.get_json()
    id_usuario = data.get('id_usuario')

    if not data:
        return jsonify({'error': 'No se recibió el ID del usuario.'}), 400

    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Usamos el marcador de posición %s para seguridad
        cursor.execute('DELETE FROM Baneo WHERE id_usu = %s', (id_usuario,))
        conn.commit()

        return jsonify({'success': True, 'mensaje': 'Usuario desbaneado correctamente.'}), 200

    except mysql.connector.Error as err:
        # Este 'except' captura errores específicos de MySQL
        print(f"Error de base de datos: {err}")
        if conn:
            conn.rollback() # Deshace cualquier cambio pendiente
        return jsonify({'error': f'Error en la base de datos: {err}'}), 500
    except Exception as e:
        # Este 'except' captura cualquier otro error inesperado
        print(f"Ocurrió un error inesperado: {e}")
        return jsonify({'error': 'Ocurrió un error interno del servidor.'}), 500
    finally:
        # Este bloque se ejecuta SIEMPRE para cerrar la conexión
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


@app.route('/get_mis_comentarios')
@login_required
def get_mis_comentarios():
    """
    Obtiene los comentarios del usuario actualmente logueado.
    """
    try:
        id_usu = current_user.id
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # Consulta para obtener los comentarios del usuario logueado
        query = """
            SELECT p.id_post, p.titulo, p.cont, u.nom_usu, p.fecha, m.nom_mat
            FROM preg p
            JOIN usuario u ON p.id_usu = u.id_usu
            JOIN materias m ON p.id_mat = m.id_mat
            WHERE p.id_usu = %s
            ORDER BY p.fecha DESC
        """
        cursor.execute(query, (id_usu,))
        comentarios = cursor.fetchall()

        cursor.close()
        conn.close()
        
        return jsonify({"success": True, "comentarios": comentarios})

    except mysql.connector.Error as err:
        print(f"Error al obtener comentarios del perfil: {err}")
        return jsonify({"success": False, "error": f"Error de base de datos: {err}"}), 500
    except Exception as e:
        print(f"Error inesperado al obtener comentarios del perfil: {e}")
        return jsonify({"success": False, "error": f"Error inesperado: {e}"}), 500

@app.route('/cambiar_avatar', methods=['POST'])
def cambiar_avatar():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No se recibieron datos"}), 400

    id_usuario = current_user.id
    valor = data.get('valorSeleccionado')

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute('UPDATE usuario SET avatar=%s WHERE id_usu=%s', (valor, id_usuario))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True})
        
    except Exception as e:
        print(f"Error inesperado: {e}")
        return jsonify({"success": False, "error": f"Error inesperado: {e}"}), 500

@app.route('/cambiar_nombre',methods=['POST'])
def cambiar_nombre():
    data=request.get_json()
    nombre_nuevo=data.get('nombre')
    password_ingresada=data.get('password')
    id_usuario=current_user.id
    if not data:
        return jsonify({'error':'faltan datos'}),500
    try:
        conn=mysql.connector.connect(**DB_CONFIG)
        cursor=conn.cursor(dictionary=True)
        cursor.execute('SELECT contraseña FROM usuario WHERE id_usu=%s',(id_usuario,))
        contra=cursor.fetchone()
        if not contra or not check_password_hash(contra['contraseña'], password_ingresada):
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'error':'contraseña incorrecta'}),500     
               
        cursor.execute('UPDATE usuario SET nom_usu=%s WHERE id_usu=%s ',(nombre_nuevo,id_usuario))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success':'nombre cambiado'})

    except Exception as e:
        print(f"Error inesperado: {e}")
        return jsonify({"success": False, "error": f"Error inesperado: {e}"}), 500
    
@app.route('/miembros')
@login_required
def nosotros():
    return render_template('index/miembros.html')


@app.route('/get_mis_likes')
@login_required
def get_mis_likes():
    """
    Obtiene los posts (preg) a los que el usuario logueado les dio like.
    """
    try:
        id_usu = current_user.id
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT p.id_post, p.titulo, p.cont, p.fecha, u.nom_usu, m.nom_mat
            FROM likes_comentarios lc
            JOIN preg p ON lc.id_post = p.id_post
            JOIN usuario u ON p.id_usu = u.id_usu
            JOIN materias m ON p.id_mat = m.id_mat
            WHERE lc.id_usu = %s
            ORDER BY p.fecha DESC
        """
        cursor.execute(query, (id_usu,))
        posts_likeados = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({"success": True, "posts": posts_likeados})

    except mysql.connector.Error as err:
        print(f"Error al obtener posts con like: {err}")
        return jsonify({"success": False, "error": f"Error de base de datos: {err}"}), 500
    except Exception as e:
        print(f"Error inesperado: {e}")
        return jsonify({"success": False, "error": f"Error inesperado: {e}"}), 500

@app.route('/mis_likes')
@login_required
@check_ban
def mis_likes():
    return render_template('index/likes.html')





if __name__ == "__main__":
    print("iniciando flask..")
    app.run(debug=True)