import json

session_data = {}

def set_session(value):
    # salvo script_id in session_data
    session_data['script_id'] = value

def get_session():
    # controllo se script_id è presente in session_data
    return session_data.get('script_id', 'unknown')

def updateScriptId(screen_id, titolo):
    # definisco il nome del file json
    json_file = "scripts.json"
    try:
        # apro il file json
        with open(json_file, 'r') as f:
            scripts_data = json.load(f)
    except FileNotFoundError:
        # Se il file non esiste, inizializzo la lista vuota
        scripts_data = []

    # cerco lo script con lo screen_id
    for script in scripts_data:
        if script["screen_id"] == screen_id:
            # se trovo il match, aggiorno il titolo
            script["titolo"] = titolo
            # aggiorno il file json
            with open(json_file, 'w') as f:
                json.dump(scripts_data, f, indent=4)
            #print(f"Titolo aggiornato per screen_id {screen_id}")
            return

    # se non trovo nessuno script con lo screen_id
    print(f"Screen_id {screen_id} non trovato.")

# creo la funzione che elimina lo script con lo screen_id specificato
def deleteScriptId(screen_id):
    # definisco il nome del file json
    json_file = "scripts.json"
    try:
        # apro il file json
        with open(json_file, 'r') as f:
            scripts_data = json.load(f)
    except FileNotFoundError:
        # Se il file non esiste, inizializzo la lista vuota
        scripts_data = []

    # cerco lo script con lo screen_id
    for script in scripts_data:
        if script["screen_id"] == screen_id:
            # se trovo il match, elimino lo script
            scripts_data.remove(script)
            # aggiorno il file json
            with open(json_file, 'w') as f:
                json.dump(scripts_data, f, indent=4)
            print(f"Script eliminato per screen_id {screen_id}")
            return

    # se non trovo nessuno script con lo screen_id
    print(f"Screen_id {screen_id} non trovato.")