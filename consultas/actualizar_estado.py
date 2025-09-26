from config import get_db
from consultas.emparejar import normalizar

def actualizar_estado_postulacion(correo_candidato, empresa, vacante, nuevo_estado):
    db_postulaciones = get_db("postulaciones")

    correo_norm = correo_candidato.strip().lower()
    empresa_norm = empresa.strip()
    vacante_norm = vacante.strip()

    result = db_postulaciones.fs.files.update_many(
        {
            "metadata.correo_candidato": correo_norm,
            "metadata.empresa": empresa_norm,
            "metadata.vacante": vacante_norm
        },
        {"$set": {"metadata.estado": nuevo_estado}}
    )

    if result.modified_count:
        print(f"✅ Estado actualizado a '{nuevo_estado}' para {correo_norm} → {empresa_norm} ({vacante_norm})")
    else:
        print(f"⚠️ No se encontró ninguna postulación que coincida con esos datos")
