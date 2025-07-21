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
            host="yamabiko.proxy.rlwy.net",
            port=36139,
            user="root",
            password="sASsCizBGUvIcNuNNknMJUgCnHKiuIgH",
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
@app.route('/informatica/4toinformatica')#el mio es el de nro (4to)
def cuarto4():
    return render_template("index/indexin4to.html")
#materias de 4to:
@app.route('/informatica/4toinformatica/labapps')
def labapps():
    id_mat=1
    return render_template("index/labapps4inf.html",id_mat=id_mat)

@app.route('/informatica/4toinformatica/labprog')
def labprog():
    id_mat=2
    return render_template("index/labprog4inf.html",id_mat=id_mat)

@app.route('/informatica/4toinformatica/labso')
def labso():
    id_mat=3
    return render_template("index/labso4inf.html",id_mat=id_mat)

@app.route('/informatica/4toinformatica/labhard')
def labhard():
    id_mat=4
    return render_template("index/labhard4inf.html",id_mat=id_mat)

@app.route('/informatica/4toinformatica/electronica')
def electronica():
    id_mat=5
    return render_template("index/electronica4inf.html",id_mat=id_mat)

@app.route('/informatica/5toinformatica')#el mio es el de nro (5to)
def quinto5():
    return render_template("index/indexin5to.html")
#materias de 5to:
@app.route('/informatica/5toinformatica/labso')
def labso5():
    id_mat=18
    return render_template("index/labso5inf.html",id_mat=id_mat)

@app.route('/informatica/5toinformatica/labhard')
def labhard5():
    id_mat=20
    return render_template("index/labhard5inf.html",id_mat=id_mat)

@app.route('/informatica/5toinformatica/labprog')
def labprog5():
    id_mat=21
    return render_template("index/labprog5inf.html",id_mat=id_mat)

@app.route('/informatica/5toinformatica/sistdig')
def labsistdig5():
    id_mat=19
    return render_template("index/labsistdig5inf.html",id_mat=id_mat)

@app.route('/informatica/5toinformatica/teleinf')
def teleinf():
    id_mat=17
    return render_template("index/teleinf5inf.html",id_mat=id_mat)

@app.route('/informatica/5toinformatica/labapss')
def labapps5():
    id_mat=22
    return render_template("index/labapps5inf.html",id_mat=id_mat)


#empieza 6to de inf


@app.route('/informatica/6toinformatica')#el mio es el de nro (6to)
def sexto6():
    return render_template("index/indexin6to.html")

@app.route('/informatica/6toinformatica/labprog')
def labprog6inf():
    id_mat=30
    return render_template("index/labprog6inf.html",id_mat=id_mat)

@app.route('/informatica/6toinformatica/labapp')
def labapp6inf():
    id_mat=31
    return render_template("index/labapp6inf.html",id_mat=id_mat)

@app.route('/informatica/6toinformatica/sisdig')
def sisdig6inf():
    id_mat=32
    return render_template("index/sisdig6inf.html",id_mat=id_mat)

@app.route('/informatica/6toinformatica/invope')
def invop6inf():
    id_mat=33
    return render_template("index/invope6inf.html",id_mat=id_mat)

@app.route('/informatica/6toinformatica/labhard')
def labhard6inf():
    id_mat=34
    return render_template("index/labhard6inf.html",id_mat=id_mat)

@app.route('/informatica/6toinformatica/seginf')
def seginf6inf():
    id_mat=35
    return render_template("index/seginf6inf.html",id_mat=id_mat)

@app.route('/informatica/6toinformatica/labso')
def labso6inf():
    id_mat=36
    return render_template("index/labso6inf.html",id_mat=id_mat)

#empieza 7mo informatica

@app.route('/informatica/7moinformatica')#el mio es el de nro (7mo)
def septimo7():
    return render_template("index/indexin7mo.html")

@app.route('/informatica/7toinformatica/proysis')
def prosis7inf():
    id_mat=45
    return render_template("index/proysis7inf.html",id_mat=id_mat)

@app.route('/informatica/7toinformatica/imyrredes')
def myredes7inf():
    id_mat=46
    return render_template("index/myrredes7inf.html",id_mat=id_mat)

@app.route('/informatica/7toinformatica/modysis')
def modysis7inf():
    id_mat=47
    return render_template("index/modysis7inf.html",id_mat=id_mat)

@app.route('/informatica/7toinformatica/evalproy')
def evalproy7inf():
    id_mat=48
    return render_template("index/evalproy7inf.html",id_mat=id_mat)

@app.route('/informatica/7toinformatica/imyrsis')
def myrsis7inf():
    id_mat=49
    return render_template("index/myrsis7inf.html",id_mat=id_mat)

@app.route('/informatica/7toinformatica/basedatos')
def bd7inf():
    id_mat=50
    return render_template("index/basdat7inf.html",id_mat=id_mat)

@app.route('/informatica/7toinformatica/empproddl')
def empproddl7inf():
    id_mat=51
    return render_template("index/empprodl7inf.html",id_mat=id_mat)

@app.route('/informatica/7toinformatica/practprof')
def practprof7inf():
    id_mat=52
    return render_template("index/practprof7inf.html",id_mat=id_mat)


@app.route('/comentario') #ruta para la página de comentarios
def indexcomentario():
    return render_template("index/indexcomentario.html")

#-A-C-A--E-M-P-I-E-Z-A--P-R-O-G-R-A-M-A-C-I-O-N--C-U-R-S-O-S
#a partir de aca son las materias de 4to programación
@app.route('/programacion/4toprogramacion') #ruta para la página de 4to de programación
def index4toprog():
    return render_template("index/indexdcuarto.html")

@app.route('/programacion/4toprogramacion/labaplicaciones')
def index4toaplicaciones():
    id_mat=1
    return render_template("index/indexlbapli.html", id_mat=id_mat)

@app.route('/programacion/4toprogramacion/labprogramacion')
def index4tolabprog():
    id_mat = 4  # ID de la materia de 4to programación
    return render_template("index/indexlbprog.html", id_mat=id_mat)

@app.route('/programacion/4toprogramacion/labsistemasoperativos')
def index4tosistop():
    id_mat = 2 
    return render_template("index/indexlbssop.html", id_mat=id_mat)

@app.route("/programacion/4toprogramacion/labhardware")
def index4tolabhardw(): 
    id_mat = 3
    return render_template("index/indexlbhardw.html", id_mat=id_mat)

@app.route("/programacion/4toprogramacion/electronica")
def index4toelectronica():
    id_mat = 5
    return render_template("index/indexelectronica.html", id_mat=id_mat)
#hasta aca son las materias de 4to programación
#-------------------------------------------------------
#a partir de aca son las materias de 5to programación
@app.route('/programacion/5toprogramacion') #ruta para la página de 5to de programación
def index5toprog():
    return render_template("index/indexdquinto.html")

@app.route('/programacion/5toprogramacion/labdiseñoweb')
def index5tolabdiseñoweb():
    id_mat = 12
    return render_template("index/labdis5prog.html", id_mat=id_mat) 

@app.route('/programacion/5toprogramacion/labprogramacion')
def index5tolabprog():
    id_mat = 11
    return render_template("index/indexlbprog.html", id_mat=id_mat)

@app.route('/programacion/5toprogramacion/sistemasdigitales')
def index5tosistemasdigitales():
    id_mat = 13
    return render_template("index/indexlbssdig.html", id_mat=id_mat)

@app.route('/programacion/5toprogramacion/labbasededatos')
def index5tolabbasededatos():
    id_mat = 14
    return render_template("index/indexlbbd.html", id_mat=id_mat)

@app.route('/programacion/5toprogramacion/labredes')
def index5tolabredes():
    id_mat = 15
    return render_template("index/indexlbredes.html", id_mat=id_mat)

@app.route('/programacion/5toprogramacion/modysistemas')
def index5tomodysistemas():
    id_mat = 16
    return render_template("index/indexmodeloss.html", id_mat=id_mat)
#hasta aca son las materias de 5to programación
#-------------------------------------------------------
#a partir de aca son las materias de 6to programación
@app.route('/programacion/6toprogramacion') #ruta para la página de 6to de programación
def index6toprog():
    return render_template("index/indexsexto.html")

@app.route('/programacion/6toprogramacion/LabSistemaGestion')
def index6toLabSistemaGestion():
    id_mat = 23
    return render_template("index/indexssdgestn.html", id_mat=id_mat)

@app.route('/programacion/6toprogramacion/LabWebDinamica')
def index6toLabWebDinamica():
    id_mat = 24
    return render_template("index/web_dinamica.html", id_mat=id_mat)

@app.route('/programacion/6toprogramacion/LabSistemasDigitales')
def index6toLabSistemasDigitales():
    id_mat = 25
    return render_template("index/indexlbssdig.html", id_mat=id_mat)

@app.route('/programacion/6toprogramacion/LabSeguridadInformática')
def index6toLabSeguridadInformática():
    id_mat = 26
    return render_template("index/indexsegurinform.html", id_mat=id_mat)

@app.route('/programacion/6toprogramacion/LabProgramacion')
def index6toLabProgramacion():
    id_mat = 27
    return render_template("index/indexlbprog.html", id_mat=id_mat)

@app.route('/programacion/6toprogramacion/LabProcesosIndustriales')
def index6toLabProcesosIndustriales():
    id_mat = 28
    return render_template("index/indexlbproc.html", id_mat=id_mat)

@app.route('/programacion/6toprogramacion/LabWebEstatica')
def index6toLabWebEstatica():
    id_mat = 24
    return render_template("index/indexwbestatc.html", id_mat=id_mat)
#hasta aca son las materias de 6to programación
#-------------------------------------------------------
#a partir de aca son las materias de 7mo programación
@app.route('/programacion/7moprogramacion') #ruta para la página de 7mo de programación
def index7moprog():
    return render_template("index/indexdseptimo.html")

@app.route('/programacion/7moprogramacion/OrgMetodos')
def index7moOrgMetodos():
    id_mat = 37
    return render_template("index/indexorgm.html", id_mat=id_mat)

@app.route('/programacion/7moprogramacion/ModSistemas')
def index7moModSistemas():
    id_mat = 38
    return render_template("index/indexmodeloss.html", id_mat=id_mat)

@app.route('/programacion/7moprogramacion/EmprProdDl')
def index7moEmprProdDl():
    id_mat = 39
    return render_template("index/indexempr.html", id_mat=id_mat)

@app.route('/programacion/7moprogramacion/EvalPytos')
def index7moEvalPytos():
    id_mat = 40
    return render_template("index/indexevaproy.html", id_mat=id_mat)

@app.route('/programacion/7moprogramacion/PytoSistWd')
def index7moPytoSistWd():
    id_mat = 41
    return render_template("index/indexpsw.html", id_mat=id_mat)

@app.route('/programacion/7moprogramacion/PdiSistComp')
def index7moPdiSistComp():
    id_mat = 42
    return render_template("index/indexpsc.html", id_mat=id_mat)

@app.route('/programacion/7moprogramacion/PdSoftPMov')
def index7moPdSoftPMov():
    id_mat = 43
    return render_template("index/indexpdspm.html", id_mat=id_mat)

@app.route('/programacion/7moprogramacion/PractProf') 
def index7moPractProf():
    id_mat = 44
    return render_template("index/indexpractprof.html", id_mat=id_mat)
#hasta aca son las materias de 7mo programación
#-------------------------------------------------------
#a partir de aca empieza el login/inicio de sesión
@app.route('/verificar', methods=['POST'])
def verificar():
    import mysql.connector
    conn = mysql.connector.connect(
        host="yamabiko.proxy.rlwy.net",
        port=36139,
        user="root",
        password="sASsCizBGUvIcNuNNknMJUgCnHKiuIgH",
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

@app.route('/comentario/materia/<int:id_mat>') 
def comentario_materia(id_mat):
    return render_template('index/indexcomentario.html', id_mat=id_mat)

@app.route('/comentario', methods=['POST']) 
def comment():
    import mysql.connector
    conn = mysql.connector.connect(
        host="yamabiko.proxy.rlwy.net",
        port=36139,
        user="root",
        password="sASsCizBGUvIcNuNNknMJUgCnHKiuIgH",
        database="railway"
    )
    try:
        data = request.get_json()
        titulo = data['titulo']
        comment = data['comment']
        id_mat=data['id_mat']
        id_usu = session.get('id_usu')  # Obtener el id del usuario de la sesión

        if not id_usu:
            return jsonify({"success": False, "error": "Usuario no autenticado"}), 401
        
        cursor = conn.cursor()
        query = "INSERT INTO preg (titulo, cont, id_mat, id_usu) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (titulo, comment, id_mat, id_usu)) # Guardar el comentario en la base de datos
        conn.commit() # Guardar los cambios en la base de datos
        cursor.close()
        conn.close() # Cerrar la conexión a la base de datos
        return jsonify({"success": True})
    except Exception as e:
        print("Error al guardar comentario:", e)  # Esto mostrará el error en la consola de Flask
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/get_comentario')
def get_comentario():
    import mysql.connector
    id_mat = request.args.get('id_mat')
    conn = mysql.connector.connect(
        host="yamabiko.proxy.rlwy.net",
        port=36139,
        user="root",
        password="sASsCizBGUvIcNuNNknMJUgCnHKiuIgH",
        database="railway"
    ) 
    cursor = conn.cursor(dictionary=True)
    if id_mat:
         cursor.execute("""
            SELECT p.id_post, p.titulo, p.cont, p.fecha, u.nom_usu AS usuario
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
        host="yamabiko.proxy.rlwy.net",
        port=36139,
        user="root",
        password="sASsCizBGUvIcNuNNknMJUgCnHKiuIgH",
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
        host="yamabiko.proxy.rlwy.net",
        port=36139,
        user="root",
        password="sASsCizBGUvIcNuNNknMJUgCnHKiuIgH",
        database="railway"
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.cont, u.nom_usu AS usuario
        FROM rta r
        LEFT JOIN usuario u ON r.id_usu = u.id_usu
        WHERE r.id_post = %s
        ORDER BY r.id_com ASC
    """, (id_post,))
    respuestas = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(respuestas)



if __name__ == "__main__":
    print("iniciando flask..")
    app.run(debug=True)