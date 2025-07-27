# archivo: app.py
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
#render_template se puede cambiar app = Flask(__name__, template_folder='mi_html')
import mysql.connector #conectar a MySQL
from werkzeug.security import generate_password_hash, check_password_hash
#para hacer un hash

app = Flask(__name__)
app.secret_key= 'mi_clave_secreta' #clave secreta para sesiones, cookies, etc.

# #     NO DARLE BOLAAAAAAAAAAAAAAAAAAAAAAAA
#db = mysql.connector.connect(
#    host="gondola.proxy.rlwy.net",
#    port=20050,           # puerto por defecto de MySQL
#   user="root",         # tu usuario (normalmente es 'root')
#    password="XGaKhmhcnmHScVRBFxukOaQkQdftuCzS",         # tu contraseña, si no tiene ponela vacía
#    database="railway"  # nombre exacto de la base de datos
#)
# # # Conexión con MySQL
# db = mysql.connector.connect(
#     host="localhost",
#     port=3306,           # puerto por defecto de MySQL
#     user="root",         # tu usuario (normalmente es 'root')
#     password="",         # tu contraseña, si no tiene ponela vacía
#     database="cet4"  # nombre exacto de la base de datos
# )

@app.route('/') #ruta para la página de inicio
def inicio():
    return render_template('index/indexprincipal.html')

@app.route('/comunicatenosotros')
def comnos():
    return render_template('index/indexcentralayuda.html')
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
        import mysql.connector
        conn = mysql.connector.connect(
            host="yamanote.proxy.rlwy.net",
            port=33483,
            user="root",
            password="BNeAADHQCVLNkxkYTyLSjUqSPVxfrWvH",
            database="railway"
        )
        #pasar datos de py a la bd
        #hay q usar el cursor bld (jaja me habia olvidado)
        cursor = conn.cursor()
        #el cursor genera una variable q apunta a donde va a mandar el dato (corte catapulta)
        #consulta = sql xd
        sql = "INSERT INTO usuario(nom_usu, email, contraseña) VALUES (%s, %s, %s)"
        #valores del %s los toma valores (los gaurda en orden)
        #esos valores tienen q coinsidir con los q guardan el coso de js
        hash_contra= generate_password_hash(contra)
        #en el hash_contra estamos diciendo que vamos a hacer -->
        #un cod secreto (hash) de los datos de la "contra"
        valores = (nombre,mail,hash_contra)
        #cursor manda los valores de sql (insert into) y los valores (valores ahr)
        cursor.execute(sql, valores)
        #guarda todo lo anterior en la bd (osea lo aplica)
        #Se cambió el conexion.commit por db.commit pq
        #en mi archivo de py usé "conexion" para declarar la base de datos 
        #pero en este python la bd está declarada como "db"   #ahora la bd esta declaarada como "conn"
        conn.commit()
        cursor.close()
        conn.close() 
        return "usuario registrado correctamente"
   except Exception as e:    
    return f"Error al registrar el usuario {e}",500  

#hasta aca es lo de crear cuenta
#________________________________

#ACA RUTASSSSSS DINAMICAAAAAAAS

#-----------------------------------------------


#rutas para las páginas de inicio de sesión
@app.route("/iniciarsesion")
def iniciarsesion():
    return render_template("index/indexiniciarsesion.html")

@app.route('/crearcuenta') #ruta para la página de registro #cambiar nombre de la ruta
def crearcuenta():
    return render_template('index/indexcrearcuenta.html')

@app.route('/indexhomeoinicio') #ruta para la página de inicio
def indexhomeoinicio():
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

#-------------------------------------------------------
#a partir de aca empieza el login/inicio de sesión
@app.route('/verificar', methods=['POST'])
def verificar():
    import mysql.connector
    conn = mysql.connector.connect(
        host="yamanote.proxy.rlwy.net",
        port=33483,
        user="root",
        password="BNeAADHQCVLNkxkYTyLSjUqSPVxfrWvH",
        database="railway"
    )
    datos = request.get_json() # Obtener los datos del JSON enviado desde el frontend
    email = datos.get('email') # Obtener el email del JSON
    contraseña = datos.get('password') # Obtener la contraseña del JSON

    print("Email recibido:", email) 
    print("Contraseña recibida:", contraseña)

    if not email or not contraseña: 
        return jsonify({"exito": False, "error": "email y contraseña son requeridos"}), 400 

    cursor = conn.cursor(dictionary=True) 
    cursor.execute("SELECT * FROM usuario WHERE email=%s", (email,)) #pide el usuario por email
    #el cursor ejecuta la consulta y devuelve un diccionario con los resultados
    usuario = cursor.fetchone() # Obtiene el primer resultado de la consulta
    cursor.close()
    conn.close() 

    if usuario and check_password_hash (usuario['contraseña'], contraseña): # Verifica si el usuario existe y si la contraseña es correcta
        session['id_usu'] = usuario['id_usu']  # Guardar el id de usuario en la sesión
        session['usuario'] = usuario['nom_usu']
        return jsonify({"exito": True}) 
    else:
        return jsonify({"exito": False})
    


#_____________________________________________________________________________________
#ACA ABAJO DE MI(? ESTABA LO DE /COMENTARIO/MATERIA/IDMAT Y /COMENTARIO METHOD=POST

@app.route('/comentario/materias/<int:id_mat>')
def comentario_materia(id_mat):
    import mysql.connector
    conn = mysql.connector.connect(
        host="yamanote.proxy.rlwy.net",
        port=33483,
        user="root",
        password="BNeAADHQCVLNkxkYTyLSjUqSPVxfrWvH",
        database="railway"
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT nom_mat FROM materias WHERE id_mat=%s", (id_mat,))
    materias = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('index/ComentariosParaTodos.html', id_mat=id_mat, materias=materias)

@app.route('/comentario/materias', methods=['POST'])
def agregar_comentario():
    import mysql.connector
    data = request.get_json()
    titulo = data['titulo']
    cont = data['comment']
    id_mat = data['id_mat']
    id_usu = session.get('id_usu') or None  # Si no hay login, pon None o 'Anónimo'
    conn = mysql.connector.connect(
        host="yamanote.proxy.rlwy.net",
        port=33483,
        user="root",
        password="BNeAADHQCVLNkxkYTyLSjUqSPVxfrWvH",
        database="railway"
    )
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO preg (titulo, cont, id_mat, id_usu) VALUES (%s, %s, %s, %s)",
        (titulo, cont, id_mat, id_usu)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})
#___________________________________________________________________________________
#ACA ARRIBA DE MI(? ESTABA LO DE /COMENTARIO/MATERIA/IDMAT Y /COMENTARIO METHOD=POST
@app.route('/get_comentario')
def get_comentario():
    import mysql.connector
    id_mat = request.args.get('id_mat')
    conn = mysql.connector.connect(
        host="yamanote.proxy.rlwy.net",
        port=33483,
        user="root",
        password="BNeAADHQCVLNkxkYTyLSjUqSPVxfrWvH",
        database="railway"
    ) 
    cursor = conn.cursor(dictionary=True)
    if id_mat:
         cursor.execute("""
            SELECT p.id_post, p.titulo, p.cont, p.fecha, u.nom_usu AS usuario, p.id_usu
            FROM preg p
            LEFT JOIN usuario u ON p.id_usu = u.id_usu
            WHERE p.id_mat=%s
            ORDER BY p.fecha DESC
        """, (id_mat,)) 
    else:
        cursor.execute("""
            SELECT p.id_post, p.titulo, p.cont, p.fecha, u.nom_usu AS usuario
            FROM preg p
            LEFT JOIN usuario u ON p.id_usu = u.id_usu
            WHERE p.id_mat=%s
            ORDER BY p.fecha DESC
        """, (id_mat,))
    comentarios = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(comentarios)

@app.route('/responder', methods=['POST'])
def responder():
    import mysql.connector
    conn = mysql.connector.connect(
        host="yamanote.proxy.rlwy.net",
        port=33483,
        user="root",
        password="BNeAADHQCVLNkxkYTyLSjUqSPVxfrWvH",
        database="railway"
    )
    data = request.get_json()
    id_post = data['id_post']
    cont = data['respuesta']
    id_usu = session.get('id_usu')# si aún no tenés login funcional, usa 'Anónimo'

    if not id_usu:
        return jsonify({"success": False, "error": "Usuario no autenticado"}), 401
    
    cursor = conn.cursor()
    query = "INSERT INTO rta (id_post, id_usu, cont) VALUES (%s, %s, %s)"
    cursor.execute(query, (id_post, id_usu, cont))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True})

@app.route('/get_respuestas/<int:id_post>')
def get_respuestas(id_post):
    import mysql.connector
    conn = mysql.connector.connect(
        host="yamanote.proxy.rlwy.net",
        port=33483,
        user="root",
        password="BNeAADHQCVLNkxkYTyLSjUqSPVxfrWvH",
        database="railway"
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.id_com, r.cont, u.nom_usu AS usuario, r.id_usu
        FROM rta r
        LEFT JOIN usuario u ON r.id_usu = u.id_usu
        WHERE r.id_post = %s
        ORDER BY r.id_com ASC
    """, (id_post,))
    respuestas = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(respuestas)

#---RUTA PARA ELIMINAR COMENTARIOS---
@app.route('/eliminar_comentario', methods=['POST'])
def eliminar_comentario():
    import mysql.connector
    data = request.get_json()
    id_post = data['id_post']
    id_usu = session.get('id_usu')
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
    cursor.execute("DELETE FROM rta WHERE id_post=%s", (id_post,))
    cursor.execute("DELETE FROM preg WHERE id_post=%s AND id_usu=%s", (id_post, id_usu))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'success': True})

#---RUTA PARA ELIMINAR RESPUESTAS---
@app.route('/eliminar_respuesta', methods=['POST'])
def eliminar_respuesta():
    import mysql.connector
    data = request.get_json()
    id_com = data['id_com']
    id_usu = session.get('id_usu')
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
    cursor.execute("DELETE FROM rta WHERE id_com=%s AND id_usu=%s", (id_com, id_usu))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'success': True})

if __name__ == "__main__":
    print("iniciando flask..")
    app.run(debug=True)