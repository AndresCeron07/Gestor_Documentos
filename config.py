from pymongo import MongoClient

MONGO_URI = "mongodb+srv://wceron_db_user:A2bdCSlMf8K2fxGi@documentos.y7e8pfp.mongodb.net/?retryWrites=true&w=majority&appName=Documentos"

def get_db(tipo):
    if tipo == "hoja_vida":
        return MongoClient(MONGO_URI)["hojas_de_vida"]
    elif tipo == "solicitud_empresa":
        return MongoClient(MONGO_URI)["solicitudes_empresas"]
    elif tipo == "postulaciones":  # ✅ Añadido para registrar postulaciones
        return MongoClient(MONGO_URI)["postulaciones"]
    else:
        raise ValueError("Tipo de documento no reconocido")
