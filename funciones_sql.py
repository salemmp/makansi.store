from flask import Flask, jsonify
import sqlite3
import json

def nuevo_producto(producto,cantidad,precio,talla,ruta_completa):
    con=sqlite3.connect('munsa.db')
    cursor=con.cursor()
    cursor.execute(""" INSERT INTO productos (producto,cantidad,precio,talla,foto) VALUES (?,?,?,?,?)
                   """,(producto,cantidad,precio,talla,ruta_completa))
    con.commit()
    con.close()


def mostrar_productos():
    con=sqlite3.connect('munsa.db')
    cursor=con.cursor()
    cursor.execute("""SELECT * FROM productos""")
    datos=cursor.fetchall()
    con.close()
    return datos



def  actualizar_producto_db(producto,cantidad,precio,talla,id):
    con=sqlite3.connect('munsa.db')
    cursor=con.cursor()
    cursor.execute(""" UPDATE productos SET producto=?,cantidad=?,precio=?,talla=? WHERE id=?""",
                   (producto,cantidad,precio,talla,id))
    con.commit()
    con.close()


def eliminar_registro_db(id):
    con=sqlite3.connect('munsa.db')
    cursor=con.cursor()
    cursor.execute(""" DELETE FROM productos WHERE id=?""",(id,))
    con.commit()
    con.close()





def mostrar_ventas():
    con=sqlite3.connect('munsa.db')
    cursor=con.cursor()
    cursor.execute("""SELECT * FROM ventas""")
    ventas_db=cursor.fetchall()
    con.close()
    return ventas_db


def nueva_venta_db(producto,talla,cantidad,fecha):
    con=sqlite3.connect('munsa.db')
    cursor=con.cursor()
    cursor.execute("""INSERT INTO ventas (producto,talla,cantidad,fecha) VALUES (?,?,?,?)""",
                   (producto,talla,cantidad,fecha))
    con.commit()
    con.close()
    

def editar_venta_db(producto,talla,cantidad,id):
    con=sqlite3.connect('munsa.db')
    cursor=con.cursor()
    cursor.execute("""UPDATE ventas SET producto=?,talla=?,cantidad=? WHERE id=?""",
                   (producto,talla,cantidad,id))
    con.commit()
    con.close()


def eliminar_venta_db(id):
    con=sqlite3.connect('munsa.db')
    cursor=con.cursor()
    cursor.execute("""DELETE FROM ventas WHERE id=?""",(id,))
    con.commit()
    con.close()



def total_ventas_db():
    con=sqlite3.connect('munsa.db')
    cursor=con.cursor()
    cursor.execute("""select producto, sum(cantidad) as cantidad_vendida,
(select precio from productos WHERE ventas.producto= producto) as precio_CU,
(sum(cantidad) *(select precio from productos WHERE ventas.producto= producto)) as recaudado
from ventas
group by producto
order by recaudado desc""")
    total_ventas=cursor.fetchall()
    con.close()
    datos_json=[]
    for registro in total_ventas:
        registro_json= {
            'producto':registro[0],
            'cantidad vendida':registro[1],
            'precio C/U':registro[2],
            'recaudado':registro[3]
        }
        datos_json.append(registro_json)

    datos_json_string=json.dumps(datos_json)
    return jsonify(datos_json_string)