import os
from flask import Flask, render_template,url_for,request,redirect,jsonify,session

import sqlite3

from funciones_sql import *
from werkzeug.utils import secure_filename
import urllib.request
import json



app = Flask(__name__)

DATABASE='munsa.db'
UPLOAD_FOLDER = 'static/uploads/'
UPLOAD        = 'uploads/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
EXTENSIONES_PERMITIDAS = set(['png', 'jpg', 'jpeg', 'gif'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY']='123'
app.config['MI_VARIABLE_PERSONAL']='SALEM'











def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in EXTENSIONES_PERMITIDAS




@app.route('/')

def  store():
   datos=mostrar_productos()
   return render_template('store/store.html',datos=datos)
  




@app.route('/productos')
def productos():
    # Si el usuario no ha pasado por el login, lo rebotamos
    if 'usuario' not in session:
        print('Debes iniciar sesión para acceder a esta sección.', 'error')
        return redirect(url_for('login'))
    
    # Aquí va tu lógica para traer los productos de la base de datos
    # Por ejemplo:
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM productos;") # Reemplaza por tu tabla real de stock
        datos = cursor.fetchall()
        conn.close()
    except sqlite3.Error:
        datos = [] # Si da error o está vacía, enviamos una lista vacía para que Jinja no rompa

    # Renderiza tu tabla pasándole los datos
    return render_template('productos.html', datos=datos)


def verificar_usuario(username, password):
    """Consulta de manera segura si las credenciales existen en SQLite."""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Consulta parametrizada para evitar inyecciones SQL
        query = "SELECT * FROM usuarios WHERE nombre = ? AND contrasena = ?"
        cursor.execute(query, (username, password))
        usuario = cursor.fetchone()
        conn.close()
        return usuario
    except sqlite3.Error as e:
        print(f"Error en la base de datos: {e}")
        return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        usuario_valido = verificar_usuario(username, password)
        
        if usuario_valido:
            # Creamos la sesión en el navegador
            session['usuario'] = username 
            # Redirige a la función 'productos' (la tabla de administración)
            return redirect(url_for('productos')) 
        else:
            print('Usuario o contraseña incorrectos', 'error')
            return redirect(url_for('login'))
            
    return render_template('login.html')



@app.route('/logout')
def logout():
    session.clear() # Borra todo el rastro de la sesión
    print('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('login'))

@app.route('/formulario',methods=['GET','POST'])
def formulario():

  if request.method=='POST':
      

      if 'file' not in request.files:
        return 'Imagen Requerida'
    

      file = request.files['file']
      if file.filename == '':
        print("no se selecciono ninguna imagen")
        return redirect(request.url)
    
    
      if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        #print('upload_image filename: ' + filename)
        ruta_completa=str(UPLOAD)+str(filename)
        producto= request.form['producto']
        cantidad= request.form['cantidad']
        precio=request.form['precio']
        talla=request.form['tallas']
        nuevo_producto(producto,cantidad,precio,talla,ruta_completa)
        return redirect(url_for('productos'))
      else:
         return 'no permitimos esos documentos'
      
  else:
      return redirect(url_for('productos'))
  

@app.route('/actualizar_producto/<id>',methods=['GET','POST'])
def actualizar_producto(id):
   
   if request.method=='POST':
      id=id
      producto= request.form['producto']
      cantidad= request.form['cantidad']
      precio=request.form['precio']
      talla=request.form['tallas']
      actualizar_producto_db(producto,cantidad,precio,talla,id)
      return redirect(url_for('productos'))
   return redirect(url_for('productos'))




@app.route('/eliminar_registro/<id>',methods=['GET','POST'])
def eliminar_registro(id):

   if request.method=='POST':
      id=id
      eliminar_registro_db(id)
      return redirect(url_for('productos'))
   return redirect(url_for('productos'))







@app.route('/ventas')
def ventas():
   # Si el usuario no ha pasado por el login, lo rebotamos
      if 'usuario' not in session:
         print('Debes iniciar sesión para acceder a esta sección.', 'error')
         return redirect(url_for('login'))
      
      # Aquí va tu lógica para traer los productos de la base de datos
      # Por ejemplo:
      try:
         conn = sqlite3.connect(DATABASE)
         cursor = conn.cursor()
         cursor.execute("SELECT * FROM productos;") # Reemplaza por tu tabla real de stock
         datos = cursor.fetchall()
         conn.close()
      except sqlite3.Error:
         datos = [] # Si da error o está vacía, enviamos una lista vacía para que Jinja no rompa


      ventas_db=mostrar_ventas()
      datos=mostrar_productos()
      # Renderiza tu tabla pasándole los datos
      return render_template('ventas.html', datos=datos,ventas_db=ventas_db)
   





@app.route('/nueva_venta',methods=['GET','POST'])
def nueva_venta():
   if request.method=='POST':
      producto=request.form['ventas_select_producto']
      talla=request.form['ventas_select_talla']
      cantidad=request.form['cantidad']
      fecha=request.form['fecha']
      nueva_venta_db(producto,talla,cantidad,fecha)
      return redirect(url_for('ventas'))
   return "no es post"



@app.route('/editar_venta/<id>',methods=['GET','POST'])
def editar_venta(id):
   if request.method=='POST':
      producto=request.form['producto']
      cantidad=request.form['cantidad']
      talla=request.form['talla']
      id=id
      editar_venta_db(producto,talla,cantidad,id)
      return redirect(url_for('ventas'))

   return redirect(url_for('ventas'))




@app.route('/eliminar_venta/<id>',methods=['GET','POST'])
def eliminar_venta(id):
   if request.method=='POST':
      id=id
      eliminar_venta_db(id)
      return redirect(url_for('ventas'))
   return redirect(url_for('ventas'))



@app.route('/estadisticas')
def estadisticas():
   # Si el usuario no ha pasado por el login, lo rebotamos
      if 'usuario' not in session:
         print('Debes iniciar sesión para acceder a esta sección.', 'error')
         return redirect(url_for('login'))
      
      # Aquí va tu lógica para traer los productos de la base de datos
      # Por ejemplo:
      try:
         conn = sqlite3.connect(DATABASE)
         cursor = conn.cursor()
         cursor.execute("SELECT * FROM productos;") # Reemplaza por tu tabla real de stock
         datos = cursor.fetchall()
         conn.close()
      except sqlite3.Error:
         datos = [] # Si da error o está vacía, enviamos una lista vacía para que Jinja no rompa


      total_ventas=total_ventas_db()
      print(total_ventas)
      # Renderiza tu tabla pasándole los datos
      return render_template('estadisticas.html',total_ventas=total_ventas)

   
   


@app.route('/usuarios')
def  usuarios():
   return render_template('working.html')





@app.route('/obtener_ventas_totales')
def obtener_ventas_totales():
    total_ventas=total_ventas_db()
    return total_ventas




if __name__ == '__main__':
    app.run(debug=True)
