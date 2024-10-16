from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import json  # Importar json para el manejo de archivos

# Inicializar FastAPI
app = FastAPI()

# Configurar la carpeta de plantillas y archivos estáticos
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Definir modelo de entrada para la API
class ContactCreate(BaseModel):
    nombre: str
    telefono: str
    email: str

# Funciones para leer y escribir en el archivo JSON
def read_contacts_json():
    try:
        with open('contacts.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def write_contacts_json(contacts):
    with open('contacts.json', 'w') as f:
        json.dump(contacts, f, indent=4)

# Rutas de la aplicación
@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/contactos/")
def listar_contactos(request: Request):
    contactos_json = read_contacts_json()  # Leer contactos desde el archivo JSON
    return templates.TemplateResponse("contactos.html", {"request": request, "contactos": contactos_json})

@app.post("/contactos/")
def agregar_contacto(contacto: ContactCreate):
    # Leer el archivo JSON, agregar el nuevo contacto y escribirlo de nuevo
    contactos_json = read_contacts_json()
    contactos_json.append(contacto.dict())
    write_contacts_json(contactos_json)

    return {"message": "Contacto agregado con éxito"}

@app.put("/contactos/{contact_id}")
def editar_contacto(contact_id: int, contacto: ContactCreate):
    contactos_json = read_contacts_json()
    
    for c in contactos_json:
        if c['nombre'] == contact_id:  # Ajusta esto según tu lógica
            c.update(contacto.dict())
            write_contacts_json(contactos_json)
            return {"message": "Contacto actualizado con éxito"}
    
    raise HTTPException(status_code=404, detail="Contacto no encontrado")

@app.delete("/contactos/{contact_id}")
def eliminar_contacto(contact_id: int):
    contactos_json = read_contacts_json()
    contactos_json = [c for c in contactos_json if c['nombre'] != contact_id]  # Ajusta esto según tu lógica
    write_contacts_json(contactos_json)

    return {"message": "Contacto eliminado con éxito"}


