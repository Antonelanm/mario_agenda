class Contact:
    def __init__(self, nombre: str, apellido: str, telefono: str, email: str):
        self.nombre = nombre
        self.apellido = apellido
        self.telefono = telefono
        self.email = email

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.telefono}, {self.email})"

class ContactManager:
    def __init__(self):
        self.contactos = []

    def editar_contacto(self, contacto_existente, nuevo_contacto: Contact):
        contacto_existente.nombre = nuevo_contacto.nombre
        contacto_existente.telefono = nuevo_contacto.telefono
        contacto_existente.email = nuevo_contacto.email

    def eliminar_contacto(self, contacto_existente):
        self.contactos.remove(contacto_existente)
