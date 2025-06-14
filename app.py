from flask import Flask, render_template, request, jsonify, redirect, url_for
import mysql.connector
app = Flask(__name__)
#conectar con mySQL
db=mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="cet4"
)

@app.route('/')
def login():
    return render_template('index/indexiniciarsesion.html')

@app.route('/verificar', methods=['POST'])
def verificar():
    datos = request.get_json()
    usuario = datos['email']
    contrasena = datos['password']

    cursor = db.cursor(dictionary=True)
    consulta = "SELECT * FROM usuarios WHERE usuario = %s AND contrasena = %s"
    cursor.execute(consulta, (usuario, contrasena))
    resultado = cursor.fetchone()
    cursor.close()

    if resultado:
        return jsonify({"exito": True})
    else:
        return jsonify({"exito": False})

@app.route('/bienvenida')
def bienvenida():
    return render_template('index/bienvenida.html')

if __name__ == '__main__':
    app.run(debug=True)