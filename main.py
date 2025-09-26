import argparse
from uploader.subir import subir_documento
from consultas.listar import listar_candidatos, listar_empresas
from consultas.emparejar import emparejar_web
from consultas.listar_postulaciones import listar_postulaciones
from consultas.actualizar_estado import actualizar_estado_postulacion
from consultas.listar_emparejamientos import listar_emparejamientos

# 🧠 Configura el parser
parser = argparse.ArgumentParser(description="Gestor de documentos MongoDB")

parser.add_argument(
    "accion",
    choices=[
        "subir_hoja_vida",
        "subir_solicitud_empresa",
        "listar_candidatos",
        "listar_empresas",
        "listar_postulaciones",
        "actualizar_estado",
        "listar_emparejamientos"
    ],
    help="Acción a ejecutar"
)

parser.add_argument("ruta", nargs="?", help="Ruta del archivo local o parámetros separados por coma")
parser.add_argument("--nombre", help="Nombre con el que se guardará el archivo")
parser.add_argument("--empresa", help="Filtrar por empresa")
parser.add_argument("--vacante", help="Filtrar por vacante")
parser.add_argument("--estado", help="Filtrar por estado")
parser.add_argument("--minimo", type=float, help="Filtrar por score mínimo")

args = parser.parse_args()

# 🧠 Ejecuta según la acción
match args.accion:
    case "subir_hoja_vida":
        subir_documento(args.ruta, args.nombre, tipo="hoja_vida")
        print("🔄 Ejecutando emparejamiento automático por candidato...")
        emparejamientos = emparejar_web("candidato")
        for r in emparejamientos:
            print(f"👤 {r['candidato']} ({r['carrera']})")
            if r["compatibles"]:
                for c in r["compatibles"]:
                    print(f"   ✅ Compatible con: {c['empresa']} ({c['score']}%)")
                    for razon in c["razones"]:
                        print(f"      🔹 {razon}")
            else:
                print("   ❌ Sin coincidencias")
            print("-" * 50)

    case "subir_solicitud_empresa":
        subir_documento(args.ruta, args.nombre, tipo="solicitud_empresa")
        print("🔄 Ejecutando emparejamiento automático por empresa...")
        emparejamientos = emparejar_web("empresa")
        for r in emparejamientos:
            print(f"🏢 {r['candidato']} ({r['vacante']})")
            if r["compatibles"]:
                for c in r["compatibles"]:
                    print(f"   ✅ Compatible con: {c['empresa']} ({c['score']}%)")
                    for razon in c["razones"]:
                        print(f"      🔹 {razon}")
            else:
                print("   ❌ Sin coincidencias")
            print("-" * 50)

    case "listar_candidatos":
        listar_candidatos()

    case "listar_empresas":
        listar_empresas()

    case "listar_postulaciones":
        listar_postulaciones()

    case "actualizar_estado":
        if args.ruta:
            partes = [p.strip() for p in args.ruta.split(",")]
            if len(partes) == 4:
                correo, empresa, vacante, nuevo_estado = partes
                actualizar_estado_postulacion(correo, empresa, vacante, nuevo_estado)
            else:
                print("⚠️ Formato incorrecto. Usa: correo,empresa,vacante,nuevo_estado")
        else:
            print("⚠️ Debes proporcionar los parámetros separados por coma")

    case "listar_emparejamientos":
        correo = args.ruta if args.ruta and "@" in args.ruta else None
        listar_emparejamientos(
            correo=correo,
            empresa=args.empresa,
            vacante=args.vacante,
            estado=args.estado,
            minimo=args.minimo,
            retornar=False
        )
