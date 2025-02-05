# 04.02.25
# Made by: @GiuPic

import json
import time
from typing import Optional

class RequestManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, json_file: str = "active_requests.json"):
        if not hasattr(self, 'initialized'):
            self.json_file = json_file
            self.initialized = True
            self.on_response_callback = None

    def create_request(self, type: str) -> str:
        request_data = {
            "type": type,
            "response": None,
            "timestamp": time.time()
        }

        with open(self.json_file, "w") as f:
            json.dump(request_data, f)

        return "Ok"

    def save_response(self, message_text: str) -> bool:
        try:
            # Carica il file JSON
            with open(self.json_file, "r") as f:
                data = json.load(f)

            # Controlla se esiste la chiave 'type' e se la risposta è presente
            if "type" in data and "response" in data:
                data["response"] = message_text  # Aggiorna la risposta

                with open(self.json_file, "w") as f:
                    json.dump(data, f, indent=4)

                return True
            else:
                return False

        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"⚠️ save_response - errore: {e}")
            return False

    def get_response(self) -> Optional[str]:
        try:
            with open(self.json_file, "r") as f:
                data = json.load(f)

                # Verifica se esiste la chiave "response"
                if "response" in data:
                    response = data["response"]  # Ottieni la risposta direttamente

                    if response is not None and self.on_response_callback:
                        self.on_response_callback(response)

                    return response

        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"get_response - errore: {e}")
        return None

    def clear_file(self) -> bool:
        try:
            with open(self.json_file, "w") as f:
                json.dump({}, f)
            print(f"File {self.json_file} è stato svuotato con successo.")
            return True
        
        except Exception as e:
            print(f"⚠️ clear_file - errore: {e}")
            return False