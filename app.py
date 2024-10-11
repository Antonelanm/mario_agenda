from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
import json  # Importar json para el manejo de archivos

# Inicializar FastAPI
app = FastAPI()

# Configuración de la base de datos
DATABASE_URL = os.environ.get("DATABASE_URL", "mysql+pymysql://root:Ant0nela@localhost/agenda_database")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelos para la base de datos
class ContactDB(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), index=True)
    telefono = Column(String(15))
    email = Column(String(50))

# Crear tablas
Base.metadata.create_all(bind=engine)

# Configurar la carpeta de plantillas y archivos estáticos
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Definir modelo de entrada para la API
class ContactCreate(BaseModel):
    nombre: str
    telefono: str
    email: str

# Obtener sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
def listar_contactos(request: Request, db: Session = Depends(get_db)):
    contactos = db.query(ContactDB).all()
    contactos_json = read_contacts_json()  # Leer contactos desde el archivo JSON
    return templates.TemplateResponse("contactos.html", {"request": request, "contactos": contactos_json})

@app.post("/contactos/")
def agregar_contacto(contacto: ContactCreate, db: Session = Depends(get_db)):
    nuevo_contacto = ContactDB(**contacto.dict())
    db.add(nuevo_contacto)
    db.commit()
    db.refresh(nuevo_contacto)

    # Leer el archivo JSON, agregar el nuevo contacto y escribirlo de nuevo
    contactos_json = read_contacts_json()
    contactos_json.append(contacto.dict())
    write_contacts_json(contactos_json)

    return {"message": "Contacto agregado con éxito"}

@app.put("/contactos/{contact_id}")
def editar_contacto(contact_id: int, contacto: ContactCreate, db: Session = Depends(get_db)):
    contacto_existente = db.query(ContactDB).filter(ContactDB.id == contact_id).first()
    if not contacto_existente:
        raise HTTPException(status_code=404, detail="Contacto no encontrado")
    contacto_existente.nombre = contacto.nombre
    contacto_existente.telefono = contacto.telefono
    contacto_existente.email = contacto.email
    db.commit()
    db.refresh(contacto_existente)

    # Actualizar contacto en el archivo JSON
    contactos_json = read_contacts_json()
    for c in contactos_json:
        if c['nombre'] == contacto_existente.nombre:
            c.update(contacto.dict())
    write_contacts_json(contactos_json)

    return {"message": "Contacto actualizado con éxito"}

@app.delete("/contactos/{contact_id}")
def eliminar_contacto(contact_id: int, db: Session = Depends(get_db)):
    contacto_existente = db.query(ContactDB).filter(ContactDB.id == contact_id).first()
    if not contacto_existente:
        raise HTTPException(status_code=404, detail="Contacto no encontrado")
    
    db.delete(contacto_existente)
    db.commit()

    # Eliminar contacto del archivo JSON
    contactos_json = read_contacts_json()
    contactos_json = [c for c in contactos_json if c['nombre'] != contacto_existente.nombre]
    write_contacts_json(contactos_json)

    return {"message": "Contacto eliminado con éxito"}

