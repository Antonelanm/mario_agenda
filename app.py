from flask import Flask, request, jsonify, flash, redirect, url_for, render_template
import mysql.connector
import json

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'

# Configuración de conexión a MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="tu_contraseña",
    database="nombre_base_datos"
)

# Ruta para la página principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para agregar un contacto
@app.route('/agregar', methods=['POST'])
def agregar_contacto():
    nombre = request.form.get('nombre')
    telefono = request.form.get('telefono')
    mail = request.form.get('mail')

    cursor = db.cursor()
    cursor.execute("INSERT INTO contactos (nombre, telefono, mail) VALUES (%s, %s, %s)", (nombre, telefono, mail))
    db.commit()
    id_contacto = cursor.lastrowid  # Obtener el último ID insertado

    # Actualizar el archivo JSON
    with open('contactos.json', 'r+') as file:
        contactos = json.load(file)
        contactos.append({'id': id_contacto, 'nombre': nombre, 'telefono': telefono, 'mail': mail})
        file.seek(0)
        file.truncate()  # Asegura que se sobrescriba el archivo
        json.dump(contactos, file, indent=4)

    flash("¡Contacto guardado con éxito!")
    return redirect(url_for('index'))

# Ruta para eliminar un contacto
@app.route('/eliminar/<int:id>', methods=['POST'])
def eliminar_contacto(id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM contactos WHERE id = %s", (id,))
    db.commit()

    # Eliminar del JSON
    with open('contactos.json', 'r+') as file:
        contactos = json.load(file)
        contactos = [c for c in contactos if c.get('id') != id]
        file.seek(0)
        file.truncate()
        json.dump(contactos, file, indent=4)

    flash("¡Contacto eliminado con éxito!")
    return redirect(url_for('index'))

# Ruta para editar un contacto
@app.route('/editar/<int:id>', methods=['POST'])
def editar_contacto(id):
    nombre = request.form.get('nombre')
    telefono = request.form.get('telefono')
    mail = request.form.get('mail')

    cursor = db.cursor()
    cursor.execute("UPDATE contactos SET nombre = %s, telefono = %s, mail = %s WHERE id = %s", (nombre, telefono, mail, id))
    db.commit()

    # Actualizar en JSON
    with open('contactos.json', 'r+') as file:
        contactos = json.load(file)
        for contacto in contactos:
            if contacto.get('id') == id:
                contacto['nombre'] = nombre
                contacto['telefono'] = telefono
                contacto['mail'] = mail
        file.seek(0)
        file.truncate()  # Asegura que se sobrescriba el archivo
        json.dump(contactos, file, indent=4)

    flash("¡Contacto editado con éxito!")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

