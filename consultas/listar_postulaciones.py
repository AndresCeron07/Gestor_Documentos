from config import get_db
from datetime import datetime

def listar_postulaciones(retornar=False, filtro_estado=None):
    db_postulaciones = get_db("postulaciones")
    archivos = db_postulaciones.fs.files.find().sort("uploadDate", -1)

    resultados = []

    for archivo in archivos:
        meta = archivo.get("metadata", {})
        estado = meta.get("estado", "Sin estado")

        if filtro_estado and filtro_estado.lower() != estado.lower():
            continue

        resultados.append({
            "fecha": meta.get("fecha", datetime.min),
            "correo": meta.get("correo_candidato", "Desconocido"),
            "empresa": meta.get("empresa", "Desconocida"),
            "vacante": meta.get("vacante", "Sin vacante"),
            "score": meta.get("score", 0),
            "estado": estado
        })

    if retornar:
        return resultados

    print("\n📄 Postulaciones registradas:\n")
    for r in resultados:
        print(f"🕒 {r['fecha'].strftime('%Y-%m-%d %H:%M')}")
        print(f"👤 Candidato: {r['correo']}")
        print(f"🏢 Empresa: {r['empresa']}")
        print(f"📌 Vacante: {r['vacante']}")
        print(f"📊 Compatibilidad: {r['score']}%")
        print(f"📍 Estado: {r['estado']}")
        print("-" * 50)
