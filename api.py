from flask import Flask 
from flask import request, jsonify, render_template
import mysql.connector
#para conectar con la bd: mysql.connector
conexion = mysql.connector.connect(
    #va una coma c/vez q pones un datito (como en mysql)
    host ="localhost",
    user ="root",
    password ="",
    database="cet4"
    #eso de arriba es para conectar con mysql (corte el mysql -u root -p)
    #password es la contraseña (osea el enter)
)
#el 2do flask se pone Flask (con mayusc pq py es maricon)
app = Flask(__name__) 
#el app= es una variable
#el =Flask(__name__) dice que va a agarrar una funcion de flask
#y que esa funcion va a usar un nombre (una ruta)
@app.route('/')
def inicio():
    return render_template('index/indexcrearcuenta.html')
#sin una / inicial antes del index/ pq ya stams en templates gracias al render_template
@app.route('/registrar',methods=['POST'])
def dataregistro():
   datosdesdejs = request.json
   #name = datosdesdejs['nombre']
   mail = datosdesdejs['email']
   contra = datosdesdejs['contra']
   confcontra = datosdesdejs['confcontra']

    #pasar datos de py a la bd
    #hay q usar el cursor bld (jaja me habia olvidado)
    cursor = conexion.cursor()
    #el cursor genera una variable q apunta a donde va a mandar el dato (corte catapulta)
    #consulta = sql xd
    sql = "INSERT INTO usuario(nom_usu, email, contraseña) VALUES (%s, %s, %s)"
    #valores del %s los toma valores (los gaurda en orden)
    #esos valores tienen q coinsidir con los q guardan el coso de js
    valores = (mail,mail,contra)
    #cursor manda los valores de sql (insert into) y los valores (valores ahr)
    cursor.execute(sql, valores)
    #guarda todo lo anterior en la bd (osea lo aplica)
    conexion.commit()
    cursor.close()
    return "usuario registrado correctamente"


#para ejecutar la mrd esa:
if __name__ == '__main__':
    app.run(debug=True)
