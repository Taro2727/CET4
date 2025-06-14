from flask import Flask 
from flask import request, jsoify, render_template
#el 2do flask se pone Flask (con mayusc pq py es maricon)
app = Flask(__name__) 
#el app= es una variable
#el =Flask(__name__) dice que va a agarrar una funcion de flask
#y que esa funcion va a usar un nombre (una ruta)
@app.route('/n')
def inicio():
    return render_template('index.html ')
