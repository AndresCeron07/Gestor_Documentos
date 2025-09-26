from config import get_db
from datetime import datetime

def registrar_postulacion(correo_candidato, correo_empresa, vacante, empresa, score):
    db_postulaciones = get_db("postulaciones")

    # 🔤 Normaliza campos clave para evitar duplicados por formato
    vacante_norm = normalizar(vacante)
    empresa_norm = normalizar(empresa)
    correo_norm = correo_candidato.strip().lower()

    ya_existe = db_postulaciones.fs.files.find_one({
        "metadata.correo_candidato": correo_norm,
        "metadata.empresa": empresa_norm,
        "metadata.vacante": vacante_norm
    })

    if ya_existe:
        print(f"⚠️ Postulación ya registrada: {correo_norm} → {empresa_norm} ({vacante_norm})")
        return

    registro = {
        "correo_candidato": correo_norm,
        "correo_empresa": correo_empresa.strip().lower(),
        "vacante": vacante,
        "empresa": empresa,
        "score": score,
        "estado": "En revisión",  # ✅ Estado inicial por defecto
        "fecha": datetime.now()
    }

    db_postulaciones.fs.files.insert_one({
        "filename": f"postulacion_{correo_norm}_{vacante_norm}",
        "metadata": registro
    })

    print(f"📨 Postulación registrada: {correo_norm} → {empresa} ({vacante}) [{score}%] — Estado: En revisión")
