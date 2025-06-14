from flask import Flask, render_template, request, jsonify, redirect, url_for

app = Flask(__name__)

# Datos falsos para login
emailcorrecto = "admin@gmail.com"
contracorrecta = "1234"

@app.route('/')
def login():
    return render_template('index/indexiniciarsesion.html')

@app.route('/verificar', methods=['POST'])
def verificar():
    datos = request.get_json()
    usuario = datos['email']
    contrasena = datos['password']

    if usuario == emailcorrecto and contrasena == contracorrecta:
        return jsonify({"exito": True})
    else:
        return jsonify({"exito": False})

@app.route('/bienvenida')
def bienvenida():
    return render_template('index/indexhomeinicio.html')

if __name__ == '__main__':
    app.run(debug=True)
