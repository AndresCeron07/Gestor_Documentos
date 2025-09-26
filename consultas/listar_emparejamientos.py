from config import get_db

def listar_emparejamientos(retornar=False, correo=None, empresa=None, vacante=None, estado=None, minimo=None):
    db = get_db("postulaciones")
    col = db["postulaciones"]
    filtros = {}

    if correo:
        filtros["correo_candidato_norm"] = correo.strip().lower()
    if empresa:
        # aceptar crudo, pero filtrar por normalizado
        filtros["empresa_norm"] = empresa.strip().lower()
    if vacante:
        filtros["vacante_norm"] = vacante.strip().lower()
    if estado:
        filtros["estado"] = estado
    if minimo is not None:
        filtros["score"] = {"$gte": minimo}

    resultados = col.find(filtros).sort("fecha", -1)

    if retornar:
        return [
            {
                "correo": r.get("correo_candidato"),
                "empresa": r.get("empresa"),
                "vacante": r.get("vacante"),
                "score": r.get("score"),
                "estado": r.get("estado"),
                "fecha": r.get("fecha")
            }
            for r in resultados
        ]
    else:
        print("\n📄 Emparejamientos registrados:\n")
        for r in resultados:
            print(f"👤 {r.get('correo_candidato')} → 🏢 {r.get('empresa')} ({r.get('vacante')})")
            print(f"   ✅ Score: {r.get('score')}% · Estado: {r.get('estado')} · Fecha: {r.get('fecha')}")
            print("-" * 50)
