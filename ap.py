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

#__________________________________
#desde acá empieza el registro 
@app.route('/crearcuenta')
def regi():
    return render_template('index/indexcrearcuenta.html')
#sin una / inicial antes del index/ pq ya stams en templates gracias al render_template
@app.route('/crearcuenta/registrar',methods=['POST'])
def dataregistro():
   datosdesdejs = request.json
   nombre = datosdesdejs['name']
   mail = datosdesdejs['email']
   contra = datosdesdejs['contra']
   confcontra = datosdesdejs['confcontra']
   #no se usan () en el if de python
   if contra != confcontra:
       return "la contraseña y la confirmación no son iguales, intente nuevamente",400

   try:    
        #pasar datos de py a la bd
        #hay q usar el cursor bld (jaja me habia olvidado)
        cursor = db.cursor()
        #el cursor genera una variable q apunta a donde va a mandar el dato (corte catapulta)
        #consulta = sql xd
        sql = "INSERT INTO usuario(nom_usu, email, contraseña) VALUES (%s, %s, %s)"
        #valores del %s los toma valores (los gaurda en orden)
        #esos valores tienen q coinsidir con los q guardan el coso de js
        valores = (nombre,mail,contra)
        #cursor manda los valores de sql (insert into) y los valores (valores ahr)
        cursor.execute(sql, valores)
        #guarda todo lo anterior en la bd (osea lo aplica)
        #Se cambió el conexion.commit por db.commit pq
        #en mi archivo de py usé "conexion" para declarar la base de datos 
        #pero en este python la bd está declarada como "db"  
        db.commit()
        cursor.close()
        return "usuario registrado correctamente"
   except Exception as e:    
    return f"Error al registrar el usuario {e}",500  

#hasta aca es lo de crear cuenta
#________________________________

@app.route("/iniciarsesion")
def iniciarsesion():
    return render_template("index/indexiniciarsesion.html")

@app.route('/crearcuenta') #ruta para la página de registro #cambiar nombre de la ruta
def crearcuenta():
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

#a partir de aca empieza el login/inicio de sesión

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
        session['id_usu'] = usuario['id_usu']  # Guardar el id de usuario en la sesión
        return jsonify({"exito": True})
    else:
        return jsonify({"exito": False})

@app.route('/comentario/materia/<int:id_mat>')
def comentario_materia(id_mat):
    return render_template('index/indexcomentario.html', id_mat=id_mat)

@app.route('/comentario', methods=['POST'])
def comment():
    try:
        data = request.get_json()
        titulo = data['titulo']
        comment = data['comment']
        id_mat=data['id_mat']
        id_usu = session.get('id_usu')  # Obtener el id del usuario de la sesión

        if not id_usu:
            return jsonify({"success": False, "error": "Usuario no autenticado"}), 401
        
        cursor = db.cursor()
        query = "INSERT INTO preg (titulo, cont, id_mat, id_usu) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (titulo, comment, id_mat, id_usu))
        db.commit()
        cursor.close()
        return jsonify({"success": True})
    except Exception as e:
        print("Error al guardar comentario:", e)  # Esto mostrará el error en la consola de Flask
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/get_comentario')
def get_comentario():
    id_mat = request.args.get('id_mat')
    cursor = db.cursor(dictionary=True)
    if id_mat:
        cursor.execute("SELECT * FROM preg WHERE id_mat=%s ORDER BY fecha DESC", (id_mat,))
    else:
        cursor.execute("SELECT * FROM preg ORDER BY fecha DESC")
    comentarios = cursor.fetchall()
    cursor.close()
    return jsonify(comentarios)

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

@app.route('/get_respuestas/<int:id_preg>')
def get_respuestas(id_preg):
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.mensaje, r.usuario
        FROM respuestas r
        WHERE r.id_comentario = %s
        ORDER BY r.id_respuesta ASC
    """, (id_preg,))
    respuestas = cursor.fetchall()
    cursor.close()
    return jsonify(respuestas)



if __name__ == "__main__":
    app.run(debug=True)