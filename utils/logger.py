from datetime import datetime

def log_event(tipo, archivo, id_doc):
    with open("eventos.log", "a") as log:
        log.write(f"[{datetime.now().isoformat()}] {tipo.upper()} - {archivo} - ID: {id_doc}\n")
