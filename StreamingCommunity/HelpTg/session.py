# 04.02.25
# Made by: @GiuPic

import json

session_data = {}

def set_session(value):
    """
    Salva lo script_id nella sessione.
    """
    session_data['script_id'] = value


def get_session():
    """
    Restituisce lo script_id dalla sessione, o 'unknown' se non presente.
    """
    return session_data.get('script_id', 'unknown')


def update_script_id(screen_id, titolo):
    """
    Aggiorna il titolo di uno script in base allo screen_id.
    """
    json_file = "scripts.json"
    try:
        # Apre il file JSON e carica i dati
        with open(json_file, 'r') as f:
            scripts_data = json.load(f)

    except FileNotFoundError:
        scripts_data = []

    # Cerca lo script con lo screen_id corrispondente
    for script in scripts_data:
        if script["screen_id"] == screen_id:

            # Se trovato, aggiorna il titolo
            script["titolo"] = titolo

            # Salva i dati aggiornati nel file JSON
            with open(json_file, 'w') as f:
                json.dump(scripts_data, f, indent=4)

            return

    print(f"Screen_id {screen_id} non trovato.")


def delete_script_id(screen_id):
    """
    Elimina uno script in base allo screen_id.
    """
    json_file = "scripts.json"
    try:
        with open(json_file, 'r') as f:
            scripts_data = json.load(f)

    except FileNotFoundError:
        scripts_data = []

    # Cerca lo script con lo screen_id corrispondente
    for script in scripts_data:
        if script["screen_id"] == screen_id:

            # Se trovato, rimuove lo script
            scripts_data.remove(script)

            with open(json_file, 'w') as f:
                json.dump(scripts_data, f, indent=4)

            print(f"Script eliminato per screen_id {screen_id}")
            return

    print(f"Screen_id {screen_id} non trovato.")