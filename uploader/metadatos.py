import os
from datetime import datetime

def generar_metadatos(ruta):
    nombre = os.path.basename(ruta)
    return {
        "nombre_original": nombre,
        "fecha_subida": datetime.utcnow().isoformat(),
        "tipo": os.path.splitext(nombre)[1].replace(".", "").upper()
    }
