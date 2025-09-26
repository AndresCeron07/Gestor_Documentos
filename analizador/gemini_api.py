import google.generativeai as genai
import json
import re

# 🔐 Configura tu clave de API de Gemini
genai.configure(api_key="AIzaSyA7LFsEb5BzbxdsP0-rKbSQM3_E0Mazin8")

# 🧼 Limpia delimitadores de código en respuestas
def limpiar_json(texto):
    return re.sub(r"^```json|```$", "", texto.strip()).strip()

# ✅ Verifica si el texto es un JSON válido
def es_json_valido(texto):
    try:
        json.loads(texto)
        return True
    except json.JSONDecodeError:
        return False

# 🧹 Preprocesa el texto para mejorar la extracción
def preprocesar_texto(texto):
    return re.sub(r"\s+", " ", texto).strip()

# 📄 Extrae datos desde una hoja de vida institucional
def extraer_datos_hoja_de_vida(texto):
    texto = preprocesar_texto(texto)
    prompt = f"""
Extrae los siguientes campos desde una hoja de vida institucional:

1. Nombre completo
2. Carrera y semestre actual
3. Número de contacto
4. Correo institucional
5. Dirección de residencia
6. Habilidades técnicas y profesionales (ej. manejo de Microsoft Office, trabajo en equipo)
7. Conocimientos específicos (ej. Python, Java, bases de datos)
8. Idiomas y nivel (ej. Inglés B2, Francés A1)

Devuélvelo en formato JSON con las siguientes claves:
- nombre
- carrera
- semestre
- telefono
- correo
- direccion
- habilidades
- conocimientos
- idiomas

Texto:
{texto}
"""
    modelo = genai.GenerativeModel("gemini-2.5-flash")
    respuesta = modelo.generate_content(prompt)
    texto_limpio = limpiar_json(respuesta.text)

    if es_json_valido(texto_limpio):
        return json.loads(texto_limpio)
    else:
        print("⚠️ Error al procesar hoja de vida. Respuesta recibida:")
        print(respuesta.text)
        return {
            "nombre": None,
            "carrera": None,
            "semestre": None,
            "telefono": None,
            "correo": None,
            "direccion": None,
            "habilidades": [],
            "conocimientos": [],
            "idiomas": []
        }

# 🏢 Extrae datos desde una solicitud empresarial
def extraer_datos_solicitud_empresa(texto):
    texto = preprocesar_texto(texto)
    prompt = f"""
Extrae los siguientes campos desde una solicitud empresarial:

- Vacante o cargo solicitado
- Requisitos del perfil (como lista)
- Nombre de la empresa
- Ubicación
- Tipo de contrato

Devuélvelo en formato JSON con las siguientes claves:
- vacante
- requisitos
- empresa
- ubicacion
- tipo_contrato

Texto:
{texto}
"""
    modelo = genai.GenerativeModel("gemini-2.5-flash")
    respuesta = modelo.generate_content(prompt)
    texto_limpio = limpiar_json(respuesta.text)

    if es_json_valido(texto_limpio):
        return json.loads(texto_limpio)
    else:
        print("⚠️ Error al procesar solicitud empresarial. Respuesta recibida:")
        print(respuesta.text)
        return {
            "vacante": None,
            "requisitos": [],
            "empresa": None,
            "ubicacion": None,
            "tipo_contrato": None
        }
