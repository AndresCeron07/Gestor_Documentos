import gridfs
import os
import time
from config import get_db
from uploader.validar import es_valido
from analizador.extraer_texto import extraer_texto
from analizador.gemini_api import extraer_datos_hoja_de_vida, extraer_datos_solicitud_empresa
from datetime import datetime
from utils.logger import log_event

def subir_documento(ruta_archivo, nombre_guardado=None, tipo="hoja_vida"):
    inicio_total = time.time()

    if not es_valido(ruta_archivo):
        print("❌ Archivo no válido. Solo se permiten PDF y DOCX.")
        return

    print(f"📂 Cargando archivo: {ruta_archivo}")
    inicio_texto = time.time()
    texto = extraer_texto(ruta_archivo)
    print(f"🧠 Extracción de texto completada en {round(time.time() - inicio_texto, 2)}s")

    print("🔍 Extrayendo metadatos con Gemini...")
    inicio_gemini = time.time()
    if tipo == "hoja_vida":
        datos_extraidos = extraer_datos_hoja_de_vida(texto)
    elif tipo == "solicitud_empresa":
        datos_extraidos = extraer_datos_solicitud_empresa(texto)
    else:
        print("⚠️ Tipo de documento no reconocido.")
        return
    print(f"📌 Datos extraídos en {round(time.time() - inicio_gemini, 2)}s")
    print("📌 Datos extraídos por Gemini:", datos_extraidos)

    print("💾 Guardando archivo en MongoDB...")
    db = get_db(tipo)
    fs = gridfs.GridFS(db)

    try:
        with open(ruta_archivo, "rb") as archivo:
            metadatos = {
                "nombre_original": os.path.basename(ruta_archivo),
                "fecha_subida": datetime.utcnow().isoformat(),
                "tipo_documento": tipo,
                "extraido": datos_extraidos
            }
            file_id = fs.put(archivo, filename=nombre_guardado or metadatos["nombre_original"], metadata=metadatos)
            print(f"✅ Documento ({tipo}) subido con datos extraídos. ID: {str(file_id)[:8]}")
            log_event("subida", ruta_archivo, file_id)
    except Exception as e:
        print("❌ Error al guardar en MongoDB:", e)
        return

    print(f"⏱️ Proceso completo en {round(time.time() - inicio_total, 2)}s")
