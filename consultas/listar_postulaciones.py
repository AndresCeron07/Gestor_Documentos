from config import get_db
from datetime import datetime

def listar_postulaciones(retornar=False, filtro_estado=None):
    db_postulaciones = get_db("postulaciones")
    col = db_postulaciones["postulaciones"]
    filtros = {}
    if filtro_estado:
        filtros["estado"] = filtro_estado
    archivos = col.find(filtros).sort("fecha", -1)

    resultados = []

    for archivo in archivos:
        resultados.append({
            "fecha": archivo.get("fecha", datetime.min),
            "correo": archivo.get("correo_candidato", "Desconocido"),
            "empresa": archivo.get("empresa", "Desconocida"),
            "vacante": archivo.get("vacante", "Sin vacante"),
            "score": archivo.get("score", 0),
            "estado": archivo.get("estado", "Sin estado")
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
