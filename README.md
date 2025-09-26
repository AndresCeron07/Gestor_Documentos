Configuración
------------

Variables de entorno requeridas:

- MONGO_URI: cadena de conexión a MongoDB
- GEMINI_API_KEY: clave de API de Google Gemini

Puedes crear un archivo `.env` en la raíz del proyecto:

```
MONGO_URI=mongodb+srv://usuario:password@cluster/db?retryWrites=true&w=majority
GEMINI_API_KEY=tu_clave
```

Instalación
-----------

```
pip install -r requirements.txt
```

Ejecución
---------

```
python app.py
```

