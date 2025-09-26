from config import get_db
from consultas.emparejar import normalizar

def actualizar_estado_postulacion(correo_candidato, empresa, vacante, nuevo_estado):
    db_postulaciones = get_db("postulaciones")
    col = db_postulaciones["postulaciones"]

    correo_norm = correo_candidato.strip().lower()
    empresa_norm = normalizar(empresa)
    vacante_norm = normalizar(vacante)

    result = col.update_many(
        {
            "correo_candidato_norm": correo_norm,
            "empresa_norm": empresa_norm,
            "vacante_norm": vacante_norm
        },
        {"$set": {"estado": nuevo_estado}}
    )

    if result.modified_count:
        print(f"✅ Estado actualizado a '{nuevo_estado}' para {correo_norm} → {empresa} ({vacante})")
    else:
        print(f"⚠️ No se encontró ninguna postulación que coincida con esos datos")
