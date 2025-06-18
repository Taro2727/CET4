# archivo: app.py
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
#render_template se puede cambiar app = Flask(__name__, template_folder='mi_html')
import mysql.connector #conectar a MySQL

app = Flask(__name__)
app.secret_key= 'mi_clave_secreta' #clave secreta para sesiones, cookies, etc.

# Conexión con MySQL
db = mysql.connector.connect(
    host="localhost",
    port=3306,           # puerto por defecto de MySQL
    user="root",         # tu usuario (normalmente es 'root')
    password="",         # tu contraseña, si no tiene ponela vacía
    database="cet4"  # nombre exacto de la base de datos
)

@app.route('/') #ruta para la página de inicio
def inicio():
    return render_template('index/indexprincipal.html')

@app.route('/iniciarsesion') #ruta para la página de inicio
def iniciarsesion():
    return render_template('index/indexiniciarsesion.html')

@app.route('/registrarse') #ruta para la página de registro #cambiar nombre de la ruta
def registrarse():
    return render_template('index/indexcrearcuenta.html')

@app.route('/indexhomeoinicio') #ruta para la página de inicio
def home():
    return render_template('index/indexhomeoinicio.html')

@app.route('/programacion') #ruta para la página de programación
def indexprogramacion():
    return render_template("index/dprogramacionindex.html")

@app.route('/informatica') #ruta para la página de informática
def indexinformatica():
    return render_template("index/dinformaticaindex.html")

@app.route('/comentario') #ruta para la página de comentarios
def indexcomentario():
    return render_template("index/indexcomentario.html")

@app.route('/4toprogramacion') #ruta para la página de 4to de programación
def index4toprog():
    return render_template("index/indexdcuarto.html")

@app.route('/5toprogramacion') #ruta para la página de 5to de programación
def index5toprog():
    return render_template("index/indexdquinto.html")

@app.route('/6toprogramacion') #ruta para la página de 6to de programación
def index6toprog():
    return render_template("index/indexsexto.html")

@app.route('/7toprogramacion') #ruta para la página de 7mo de programación
def index7toprog():
    return render_template("index/indexdseptimo.html")

@app.before_request
def cargar_usuario_de_prueba():
    session['usuario'] = 'UsuarioDePrueba'

@app.route('/verificar', methods=['POST'])
def verificar():
    datos = request.get_json()
    email = datos.get('email')
    contraseña = datos.get('password')

    print("Email recibido:", email)
    print("Contraseña recibida:", contraseña)

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuario WHERE email=%s AND contraseña=%s", (email, contraseña))
    usuario = cursor.fetchone()
    cursor.close()

    if usuario:
        return jsonify({"exito": True})
    else:
        return jsonify({"exito": False})

@app.route('/comentario', methods=['POST'])
def comment():
    try:
        data = request.get_json()
        comment = data['comment']
        cursor = db.cursor()
        query = "INSERT INTO preg (cont, titulo) VALUES (%s)"
        cursor.execute(query, (comment,))
        db.commit()
        cursor.close()
        return jsonify({"success": True})
    except Exception as e:
        print("Error al guardar comentario:", e)  # Esto mostrará el error en la consola de Flask
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/get_comentario')
def get_comentario():
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT cont, fecha FROM preg ORDER BY fecha DESC")
        comentarios = cursor.fetchall()
        cursor.close()
        return jsonify(comentarios)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    
@app.route('/responder', methods=['POST'])
def responder():
    data = request.get_json()
    id_comentario = data['id_comentario']
    respuesta = data['respuesta']
    usuario = session.get('usuario', 'Anónimo')  # si aún no tenés login funcional, usa 'Anónimo'

    cursor = db.cursor()
    query = "INSERT INTO respuestas (id_comentario, usuario, mensaje) VALUES (%s, %s, %s)"
    cursor.execute(query, (id_comentario, usuario, respuesta))
    db.commit()
    cursor.close()
    return jsonify({"success": True})


if __name__ == "__main__":
    app.run(debug=True)