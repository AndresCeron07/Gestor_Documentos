from pymongo import MongoClient, ASCENDING
import os

# Único cliente global reutilizable por proceso
_mongo_client = None

def _get_client():
    global _mongo_client
    if _mongo_client is None:
        mongo_uri = os.getenv("MONGO_URI")
        if not mongo_uri:
            raise RuntimeError("MONGO_URI no está definido en el entorno")
        _mongo_client = MongoClient(mongo_uri)
    return _mongo_client

def get_db(tipo):
    if tipo == "hoja_vida":
        return _get_client()["hojas_de_vida"]
    elif tipo == "solicitud_empresa":
        return _get_client()["solicitudes_empresas"]
    elif tipo == "postulaciones":
        db = _get_client()["postulaciones"]
        # Índices recomendados
        try:
            db["postulaciones"].create_index(
                [("correo_candidato_norm", ASCENDING), ("empresa_norm", ASCENDING), ("vacante_norm", ASCENDING)],
                unique=True,
                name="uniq_candidato_empresa_vacante"
            )
            db["postulaciones"].create_index([("estado", ASCENDING)], name="idx_estado")
            db["postulaciones"].create_index([("score", ASCENDING)], name="idx_score")
            db["postulaciones"].create_index([("fecha", ASCENDING)], name="idx_fecha")
        except Exception:
            pass
        return db
    else:
        raise ValueError("Tipo de documento no reconocido")
