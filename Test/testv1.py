import os
import glob
import importlib
import logging
from rich.console import Console


from Src.Api.Template.Class.SearchType import MediaManager


console = Console()

def load_search_functions():
    modules = []
    loaded_functions = {}

    # Traverse the Api directory
    api_dir = os.path.join(os.path.dirname(__file__), 'Src', 'Api')
    init_files = glob.glob(os.path.join(api_dir, '*', '__init__.py'))
    
    logging.info(f"Base folder path: {api_dir}")
    logging.info(f"Api module path: {init_files}")

    # Retrieve modules and their indices
    for init_file in init_files:
        # Get folder name as module name
        module_name = os.path.basename(os.path.dirname(init_file))
        logging.info(f"Load module name: {module_name}")

        try:
            # Dynamically import the module
            mod = importlib.import_module(f'Src.Api.{module_name}')
            # Get 'indice' from the module
            indice = getattr(mod, 'indice', 0)
            is_deprecate = bool(getattr(mod, '_deprecate', True))
            use_for = getattr(mod, '_useFor', 'other')

            if not is_deprecate:
                modules.append((module_name, indice, use_for))

        except Exception as e:
            console.print(f"[red]Failed to import module {module_name}: {str(e)}")

    # Sort modules by 'indice'
    modules.sort(key=lambda x: x[1])

    # Load search functions in the sorted order
    for module_name, _, use_for in modules:
        # Construct a unique alias for the module
        module_alias = f'{module_name}_search'
        logging.info(f"Module alias: {module_alias}")

        try:
            # Dynamically import the module
            mod = importlib.import_module(f'Src.Api.{module_name}')

            # Get the search function from the module (assuming the function is named 'search' and defined in __init__.py)
            search_function = getattr(mod, 'search')

            # Add the function to the loaded functions dictionary
            loaded_functions[module_alias] = (search_function, use_for)

        except Exception as e:
            console.print(f"[red]Failed to load search function from module {module_name}: {str(e)}")

    return loaded_functions


def search_all_sites(loaded_functions, search_string, max_sites=2):
    total_len_database = 0
    site_count = 0  # Per tenere traccia del numero di siti elaborati

    # Loop attraverso tutte le funzioni di ricerca caricate e eseguirle con la stessa stringa di ricerca
    for module_alias, (search_function, use_for) in loaded_functions.items():
        # Limita il numero di siti da cui eseguire la ricerca
        if max_sites is not None and site_count >= max_sites:
            break

        console.print(f"\n[blue]Searching in module: {module_alias} [white](Use for: {use_for})")
        
        try:
            # Esegui la funzione di ricerca con 'get_onylDatabase=True' per ottenere solo la lunghezza del database
            database: MediaManager = search_function(search_string, get_onylDatabase=True)  # Usa get_onylDatabase=True
            len_database = len(database.media_list)

            for element in database.media_list:
                print(element.__dict__)

            console.print(f"[green]Database length for {module_alias}: {len_database}")
            total_len_database += len_database  # Aggiungi il risultato al totale
            site_count += 1  # Incrementa il contatore dei siti

        except Exception as e:
            console.print(f"[red]Error while executing search function for {module_alias}: {str(e)}")

    # Restituisce la lunghezza totale di tutti i database combinati
    return total_len_database



# Example: Load the search functions, perform the search with a given string, and return the total len_database
search_string = "cars"  # The search string you'd like to use
loaded_functions = load_search_functions()
total_len = search_all_sites(loaded_functions, search_string)

console.print(f"\n[cyan]Total number of results from all sites: {total_len}")
