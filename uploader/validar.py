import os

def es_valido(ruta):
    ext = os.path.splitext(ruta)[1].lower()
    return ext in [".pdf", ".docx"]
