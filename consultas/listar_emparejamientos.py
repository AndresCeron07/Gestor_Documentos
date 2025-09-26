from config import get_db

def listar_emparejamientos(retornar=False, correo=None, empresa=None, vacante=None, estado=None, minimo=None):
    db = get_db("postulaciones")
    filtros = {}

    if correo:
        filtros["metadata.correo_candidato"] = correo.strip().lower()
    if empresa:
        filtros["metadata.empresa"] = empresa.strip().lower()
    if vacante:
        filtros["metadata.vacante"] = vacante.strip().lower()
    if estado:
        filtros["metadata.estado"] = estado
    if minimo is not None:
        filtros["metadata.score"] = {"$gte": minimo}

    resultados = db.fs.files.find(filtros)

    if retornar:
        return [
            {
                "correo": r.metadata.get("correo_candidato"),
                "empresa": r.metadata.get("empresa"),
                "vacante": r.metadata.get("vacante"),
                "score": r.metadata.get("score"),
                "estado": r.metadata.get("estado"),
                "fecha": r.metadata.get("fecha")
            }
            for r in resultados
        ]
    else:
        print("\n📄 Emparejamientos registrados:\n")
        for r in resultados:
            m = r.get("metadata", {})
            print(f"👤 {m.get('correo_candidato')} → 🏢 {m.get('empresa')} ({m.get('vacante')})")
            print(f"   ✅ Score: {m.get('score')}% · Estado: {m.get('estado')} · Fecha: {m.get('fecha')}")
            print("-" * 50)
