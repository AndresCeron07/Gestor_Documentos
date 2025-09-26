import gridfs
from config import get_db
from utils.logger import log_event

def descargar_documento(nombre_archivo, ruta_destino, tipo="hoja_vida"):
    db = get_db(tipo)
    fs = gridfs.GridFS(db)
    archivo = fs.find_one({"filename": nombre_archivo})

    if archivo:
        with open(ruta_destino, "wb") as f:
            f.write(archivo.read())
        print(f"✅ Documento descargado en: {ruta_destino}")
        log_event("descarga", nombre_archivo, str(archivo._id))
    else:
        print("❌ Archivo no encontrado.")
