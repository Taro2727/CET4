# archivo: app.py
from flask import Flask, request, jsonify, render_template 
#render_template se puede cambiar app = Flask(__name__, template_folder='mi_html')
import mysql.connector #conectar a MySQL
from flask import Blueprint 

app = Flask(__name__)

# Conexión con MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",         # tu usuario (normalmente es 'root')
    password="",         # tu contraseña, si no tiene ponela vacía
    database="cet4"  # nombre exacto de la base de datos
)

@app.route('/')
def indexhomeinicio():
    return render_template("index/indexhomeoinicio.html")

@app.route('/comment', methods=['POST'])
def comment():
    try:
        data = request.get_json() #get agarra los datos de js y los json los traduce
        comment = data['comment']
        cursor = db.cursor() #cursor para ejecutar consultas
        query = "INSERT INTO comentarios (mensaje) VALUES (%s)" # consulta SQL para insertar datos (query es una variable)
        cursor.execute(query, (comment,))
        db.commit() #guarda los cambios en la base de datos permanentemente
        cursor.close()#cierra consulta

        return jsonify({"success": True})# devuelve un JSON con el éxito de la operación
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500 # devuelve un JSON con el error en caso de que falle, 500 es un error interno del servidor

@app.route('/get_comments')#pide todos los comentarios guardados
def get_comments():
    try:
        cursor = db.cursor(dictionary=True)# cursor con diccionario para que los resultados se devuelvan como diccionarios
        cursor.execute("SELECT mensaje, fecha FROM comentarios ORDER BY fecha DESC") # consulta SQL para obtener todos los comentarios ordenados por fecha descendente
        comentarios = cursor.fetchall()#trae los resultados de la consulta
        cursor.close()
        return jsonify(comentarios)#devuelve los comentarios en formato JSON para que js los pueda mostrar
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)