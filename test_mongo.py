from pymongo import MongoClient

uri = "mongodb+srv://wceron_db_user:A2bdCSlMf8K2fxGi@documentos.y7e8pfp.mongodb.net/?retryWrites=true&w=majority&appName=Documentos"
client = MongoClient(uri)

try:
    print("✅ Conexión exitosa. Bases disponibles:", client.list_database_names())
except Exception as e:
    print("❌ Error de conexión:", e)