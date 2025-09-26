from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime
import gridfs
from bson import ObjectId

# 📦 Módulos institucionales
from config import get_db
from consultas.listar import listar_candidatos, listar_empresas
from consultas.listar_postulaciones import listar_postulaciones
from consultas.actualizar_estado import actualizar_estado_postulacion
from consultas.emparejar import emparejar_individual_candidato, emparejar_individual_empresa

# 🧠 IA y extracción
from analizador.extraer_texto import extraer_texto
from analizador.gemini_api import (
    extraer_datos_hoja_de_vida,
    extraer_datos_solicitud_empresa
)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB

# 🏠 Página principal con métricas
@app.route("/")
def index():
    db_candidatos = get_db("hoja_vida")
    db_empresas = get_db("solicitud_empresa")
    db_postulaciones = get_db("postulaciones")

    return render_template("index.html",
        total_candidatos=db_candidatos.fs.files.count_documents({}),
        total_empresas=db_empresas.fs.files.count_documents({}),
        total_postulaciones=db_postulaciones["postulaciones"].count_documents({})
    )

# 👤 Vista de candidatos
@app.route("/candidatos")
def candidatos():
    carrera = request.args.get("carrera")
    candidatos = listar_candidatos(retornar=True, filtro_carrera=carrera)
    return render_template("candidatos.html", candidatos=candidatos)

# 🏢 Vista de empresas
@app.route("/empresas")
def empresas():
    empresas = listar_empresas(retornar=True)
    return render_template("empresas.html", empresas=empresas)

# 📄 Vista de postulaciones
@app.route("/postulaciones")
def postulaciones():
    estado = request.args.get("estado")
    postulaciones = listar_postulaciones(retornar=True, filtro_estado=estado)
    return render_template("postulaciones.html", postulaciones=postulaciones)

# 🔄 Actualizar estado de postulación
@app.route("/actualizar", methods=["POST"])
def actualizar():
    actualizar_estado_postulacion(
        request.form["correo"],
        request.form["empresa"],
        request.form["vacante"],
        request.form["estado"]
    )
    return redirect(url_for("postulaciones"))

# 📤 Vista del formulario de carga
@app.route("/subir")
def subir():
    return render_template("subir.html")

# 📥 Procesar carga múltiple con análisis semántico y emparejamiento individual
@app.route("/subir_hojas", methods=["POST"])
def subir_hojas():
    tipo = request.form["tipo"]
    archivos = request.files.getlist("archivo[]")

    db = get_db("hoja_vida" if tipo == "hoja_vida" else "solicitud_empresa")
    fs = gridfs.GridFS(db)

    nombres_subidos = []
    emparejamientos = []

    for archivo in archivos:
        nombre = archivo.filename
        if not nombre:
            continue

        archivo.seek(0)
        texto = extraer_texto(archivo)

        datos = (
            extraer_datos_hoja_de_vida(texto)
            if tipo == "hoja_vida"
            else extraer_datos_solicitud_empresa(texto)
        )

        archivo.seek(0)
        file_id = fs.put(archivo, filename=nombre, metadata={
            "tipo_documento": tipo,
            "fecha_subida": datetime.utcnow().isoformat(),
            "extraido": datos
        })

        doc = fs.get(file_id)
        nombres_subidos.append(nombre)

        emparejamientos.append(
            emparejar_individual_candidato(doc)
            if tipo == "hoja_vida"
            else emparejar_individual_empresa(doc)
        )

    return render_template("confirmacion_multiple.html",
        tipo=tipo,
        nombres=nombres_subidos,
        emparejamientos=emparejamientos,
        modo="candidato" if tipo == "hoja_vida" else "empresa"
    )

# 🔗 Vista de emparejamientos agregados
@app.route("/emparejamientos")
def emparejamientos():
    from consultas.emparejar import emparejar_web
    modo = request.args.get("modo", "candidato")
    minimo = request.args.get("minimo", type=float, default=0)
    resultados = emparejar_web(modo)
    # Obtener también el otro modo para la plantilla compuesta
    resultados_alt = emparejar_web("empresa" if modo == "candidato" else "candidato")
    return render_template(
        "emparejamientos.html",
        resultados_candidatos=resultados if modo == "candidato" else resultados_alt,
        resultados_empresas=resultados if modo == "empresa" else resultados_alt,
        minimo=minimo,
        carrera=request.args.get("carrera"),
        vacante=request.args.get("vacante")
    )

# ✅ Confirmación visual tras carga múltiple
@app.route("/confirmacion_multiple")
def confirmacion_multiple():
    return render_template("confirmacion_multiple.html",
        tipo=request.args.get("tipo"),
        nombres=request.args.getlist("nombres")
    )

# 🧾 Visualización de perfil individual
@app.route("/perfil/<file_id>")
def perfil(file_id):
    db = get_db("hoja_vida")
    fs = gridfs.GridFS(db)
    archivo = fs.find_one({"_id": ObjectId(file_id)})

    if not archivo:
        return "Perfil no encontrado", 404

    return render_template("perfil.html",
        datos=archivo.metadata.get("extraido", {}),
        nombre=archivo.filename,
        file_id=file_id
    )

# ✏️ Editar perfil de candidato
@app.route("/perfil/<file_id>/editar", methods=["POST"])
def editar_perfil(file_id):
    db = get_db("hoja_vida")
    # Parseo de listas separadas por coma
    def parse_list(valor):
        if not valor:
            return []
        return [v.strip() for v in valor.split(",") if v.strip()]

    set_ops = {
        "metadata.extraido.nombre": request.form.get("nombre") or None,
        "metadata.extraido.carrera": request.form.get("carrera") or None,
        "metadata.extraido.semestre": request.form.get("semestre") or None,
        "metadata.extraido.telefono": request.form.get("telefono") or None,
        "metadata.extraido.correo": request.form.get("correo") or None,
        "metadata.extraido.direccion": request.form.get("direccion") or None,
        "metadata.extraido.habilidades": parse_list(request.form.get("habilidades")),
        "metadata.extraido.conocimientos": parse_list(request.form.get("conocimientos")),
        "metadata.extraido.idiomas": parse_list(request.form.get("idiomas"))
    }

    db.fs.files.update_one({"_id": ObjectId(file_id)}, {"$set": set_ops})
    return redirect(url_for("perfil", file_id=file_id))

# 🧾 Perfil de empresa con top 10 candidatos
@app.route("/empresa/<file_id>")
def perfil_empresa(file_id):
    from consultas.emparejar import calcular_top_candidatos_para_empresa
    db = get_db("solicitud_empresa")
    fs = gridfs.GridFS(db)
    archivo = fs.find_one({"_id": ObjectId(file_id)})
    if not archivo:
        return "Empresa no encontrada", 404
    datos = archivo.metadata.get("extraido", {})
    resultado = calcular_top_candidatos_para_empresa(archivo, limite=10)
    return render_template("perfil_empresa.html",
        empresa=resultado.get("empresa"),
        vacante=resultado.get("vacante"),
        correo=resultado.get("correo"),
        top=resultado.get("top", []),
        extraido=datos,
        file_id=file_id
    )

# ✏️ Editar perfil de empresa
@app.route("/empresa/<file_id>/editar", methods=["POST"])
def editar_perfil_empresa(file_id):
    db = get_db("solicitud_empresa")
    def parse_list(valor):
        if not valor:
            return []
        return [v.strip() for v in valor.split(",") if v.strip()]

    set_ops = {
        "metadata.extraido.empresa": request.form.get("empresa") or None,
        "metadata.extraido.vacante": request.form.get("vacante") or None,
        "metadata.extraido.requisitos": parse_list(request.form.get("requisitos")),
        "metadata.extraido.ubicacion": request.form.get("ubicacion") or None,
        "metadata.extraido.tipo_contrato": request.form.get("tipo_contrato") or None,
        "metadata.extraido.correo": request.form.get("correo") or None
    }

    db.fs.files.update_one({"_id": ObjectId(file_id)}, {"$set": set_ops})
    return redirect(url_for("perfil_empresa", file_id=file_id))

# 🚀 Ejecutar servidor
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)