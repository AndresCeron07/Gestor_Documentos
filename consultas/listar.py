from config import get_db
from consultas.emparejar import normalizar

# 👤 Listado de candidatos
def listar_candidatos(retornar=False, filtro_carrera=None):
    db_candidatos = get_db("hoja_vida")
    hojas = db_candidatos.fs.files.find().sort("uploadDate", -1)

    resultados = []

    for hoja in hojas:
        meta = hoja.get("metadata", {}).get("extraido", {})
        nombre = meta.get("nombre", "Sin nombre")
        carrera = meta.get("carrera", "Sin carrera")
        correo = meta.get("correo", "Sin correo")

        if filtro_carrera:
            if normalizar(filtro_carrera) not in normalizar(carrera):
                continue

        resultados.append({
            "_id": str(hoja["_id"]),  # 🔗 Para generar enlace a perfil
            "nombre": nombre,
            "carrera": carrera,
            "correo": correo
        })

    if retornar:
        return resultados

    print("\n👤 Candidatos registrados:\n")
    for r in resultados:
        print(f"🧑 {r['nombre']} — {r['carrera']} — {r['correo']}")


# 🏢 Listado de empresas
def listar_empresas(retornar=False, filtro_vacante=None):
    db_empresas = get_db("solicitud_empresa")
    solicitudes = db_empresas.fs.files.find().sort("uploadDate", -1)

    resultados = []

    for solicitud in solicitudes:
        meta = solicitud.get("metadata", {}).get("extraido", {})
        empresa = meta.get("empresa", "Empresa sin nombre")
        vacante = meta.get("vacante", "Sin vacante")
        correo = meta.get("correo", "Sin correo")

        if filtro_vacante:
            if normalizar(filtro_vacante) not in normalizar(vacante):
                continue

        resultados.append({
            "_id": str(solicitud["_id"]),  # 🔗 Para generar enlace a perfil empresarial
            "empresa": empresa,
            "vacante": vacante,
            "correo": correo
        })

    if retornar:
        return resultados

    print("\n🏢 Empresas registradas:\n")
    for r in resultados:
        print(f"🏢 {r['empresa']} — {r['vacante']} — {r['correo']}")