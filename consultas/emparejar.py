from config import get_db
from datetime import datetime, timezone
import unicodedata
from difflib import SequenceMatcher
import gridfs
from pymongo.errors import DuplicateKeyError

# 🔤 Normaliza texto eliminando acentos y convirtiendo a minúsculas
def normalizar(texto):
    if not texto:
        return ""
    return unicodedata.normalize("NFKD", str(texto).lower()).encode("ASCII", "ignore").decode("utf-8")

# 🔍 Evalúa similitud entre dos textos con umbral configurable
def similar(a, b, threshold=0.6):
    return SequenceMatcher(None, a, b).ratio() >= threshold

# ✅ Verifica si hay coincidencia entre un valor y una lista de textos
def coincide(valor, lista, threshold=0.6):
    return any(similar(valor, r, threshold) for r in lista)

# 📄 Extrae perfil de documento
def extraer_perfil(doc):
    # Soporta GridOut (doc.metadata) o dict de fs.files (doc["metadata"])        
    datos = getattr(doc, "metadata", None) or doc.get("metadata", {})
    nombre = datos.get("nombre", "Sin nombre")
    correo_raw = datos.get("correo")
    correo = correo_raw.strip().lower() if correo_raw else f"{normalizar(nombre).replace(' ', '_')}@demo.local"
    carrera = normalizar(datos.get("carrera", ""))
    conocimientos = [normalizar(c) for c in datos.get("conocimientos", [])]
    return nombre, correo, carrera, conocimientos

# 📄 Extrae datos de vacante
def extraer_vacante(doc):
    datos = getattr(doc, "metadata", None) or doc.get("metadata", {})
    empresa = datos.get("empresa", "Empresa sin nombre")
    vacante = datos.get("vacante", "Sin vacante")
    vacante_norm = normalizar(vacante)
    requisitos = [normalizar(r) for r in datos.get("requisitos", [])]
    contexto = requisitos + [vacante_norm]
    correo_empresa = datos.get("correo", "sin_correo@demo.local")
    return empresa, vacante, vacante_norm, contexto, correo_empresa

# 📨 Registra una postulación evitando duplicados
def registrar_postulacion(correo_candidato, correo_empresa, vacante, empresa, score):
    db = get_db("postulaciones")
    col = db["postulaciones"]
    vacante_norm = normalizar(vacante)
    empresa_norm = normalizar(empresa)
    correo_norm = (correo_candidato or "").strip().lower() or "sin_correo@demo.local"

    doc = {
        "correo_candidato": correo_candidato,
        "correo_candidato_norm": correo_norm,
        "correo_empresa": (correo_empresa or "").strip().lower(),
        "empresa": empresa,
        "empresa_norm": empresa_norm,
        "vacante": vacante,
        "vacante_norm": vacante_norm,
        "score": score,
        "estado": "En revisión",
        "fecha": datetime.now(timezone.utc)
    }

    try:
        col.insert_one(doc)
        return True
    except DuplicateKeyError:
        return False

# 🧠 Evalúa compatibilidad entre perfil y contexto
def evaluar_compatibilidad(carrera, conocimientos, contexto, vacante):
    score = 0
    razones = []

    if coincide(carrera, contexto):
        score += 2
        razones.append(f"Carrera compatible con vacante: {vacante}")

    conocimientos_match = [c for c in conocimientos if coincide(c, contexto)]
    score += len(conocimientos_match)
    razones += [f"Conocimiento compatible: {c}" for c in conocimientos_match]

    total_items = len(contexto) or 1
    score_pct = round((score / total_items) * 100, 2)

    return score, score_pct, razones

# 🔄 Emparejamiento masivo (manual)
def emparejar_web(modo="candidato"):
    db_candidatos = get_db("hoja_vida")
    db_empresas = get_db("solicitud_empresa")

    # Leer solo metadatos, evitar fs.get para rendimiento
    fuentes = list(db_candidatos.fs.files.find({}, {"metadata": 1, "filename": 1})) if modo == "candidato" else list(db_empresas.fs.files.find({}, {"metadata": 1, "filename": 1}))
    destinos = list(db_empresas.fs.files.find({}, {"metadata": 1, "filename": 1})) if modo == "candidato" else list(db_candidatos.fs.files.find({}, {"metadata": 1, "filename": 1}))

    resultados = []

    for fuente in fuentes:
        nombre, correo, carrera, conocimientos = extraer_perfil(fuente)
        compatibles = []

        for destino in destinos:
            empresa, vacante, vacante_norm, contexto, correo_empresa = extraer_vacante(destino)
            score, score_pct, razones = evaluar_compatibilidad(carrera, conocimientos, contexto, vacante_norm)

            if score >= 2:
                registrado = registrar_postulacion(correo, correo_empresa, vacante, empresa, score_pct)

                if registrado:
                    compatibles.append({
                        "empresa": empresa if modo == "candidato" else nombre,
                        "vacante": vacante,
                        "correo": correo,
                        "score": score_pct,
                        "razones": razones
                    })

        resultados.append({
            "candidato": nombre if modo == "candidato" else empresa,
            "vacante": vacante if modo == "empresa" else None,
            "correo": correo,
            "carrera": carrera,
            "compatibles": compatibles
        })

    return resultados

# 🔄 Emparejamiento individual por candidato
def emparejar_individual_candidato(doc):
    nombre, correo, carrera, conocimientos = extraer_perfil(doc)
    db_empresas = get_db("solicitud_empresa")
    empresas = list(db_empresas.fs.files.find({}, {"metadata": 1, "filename": 1}))

    resultados = []

    for destino in empresas:
        empresa, vacante, vacante_norm, contexto, correo_empresa = extraer_vacante(destino)
        score, score_pct, razones = evaluar_compatibilidad(carrera, conocimientos, contexto, vacante_norm)

        if score >= 2:
            registrado = registrar_postulacion(correo, correo_empresa, vacante, empresa, score_pct)
            if registrado:
                resultados.append({
                    "empresa": empresa,
                    "vacante": vacante,
                    "score": score_pct,
                    "razones": razones
                })

    return {
        "candidato": nombre,
        "carrera": carrera,
        "correo": correo,
        "compatibles": resultados
    }

# 🔄 Emparejamiento individual por empresa
def emparejar_individual_empresa(doc):
    empresa, vacante, vacante_norm, contexto, correo_empresa = extraer_vacante(doc)
    db_candidatos = get_db("hoja_vida")
    candidatos = list(db_candidatos.fs.files.find({}, {"metadata": 1, "filename": 1}))

    resultados = []

    for destino in candidatos:
        nombre, correo, carrera, conocimientos = extraer_perfil(destino)
        score, score_pct, razones = evaluar_compatibilidad(carrera, conocimientos, contexto, vacante_norm)

        if score >= 2:
            registrado = registrar_postulacion(correo, correo_empresa, vacante, empresa, score_pct)
            if registrado:
                resultados.append({
                    "nombre": nombre,
                    "correo": correo,
                    "score": score_pct,
                    "razones": razones
                })

    return {
        "empresa": empresa,
        "vacante": vacante,
        "correo": correo_empresa,
        "compatibles": resultados
    }

# 🖥️ Consola: Emparejamiento masivo
def emparejar_desde_consola(modo="candidato"):
    resultados = emparejar_web(modo)
    print(f"\n🔗 Emparejamientos por {modo}:\n")
    for r in resultados:
        print(f"{'👤' if modo == 'candidato' else '🏢'} {r['candidato']} ({r['carrera']})")
        if r["compatibles"]:
            for c in r["compatibles"]:
                print(f"   ✅ Compatible con: {c['empresa']} ({c['score']}%)")
                for razon in c["razones"]:
                    print(f"      🔹 {razon}")
        else:
            print("   ❌ Sin coincidencias")
        print("-" * 50)
