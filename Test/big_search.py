# 12.11.24

# Fix import
import os
import sys
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(src_path)


# Other
import glob
import logging
import importlib
from rich.console import Console


# Other import
from StreamingCommunity.Src.Api.Template.Class.SearchType import MediaManager


# Variable
console = Console()


def load_search_functions():
    modules = []
    loaded_functions = {}

    # Traverse the Api directory
    api_dir = os.path.join(os.path.dirname(__file__), '..', 'StreamingCommunity', 'Src', 'Api', 'Site')
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
            mod = importlib.import_module(f'StreamingCommunity.Src.Api.Site.{module_name}')

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
            mod = importlib.import_module(f'StreamingCommunity.Src.Api.Site.{module_name}')

            # Get the search function from the module (assuming the function is named 'search' and defined in __init__.py)
            search_function = getattr(mod, 'search')

            # Add the function to the loaded functions dictionary
            loaded_functions[module_alias] = (search_function, use_for)

        except Exception as e:
            console.print(f"[red]Failed to load search function from module {module_name}: {str(e)}")

    return loaded_functions


def search_all_sites(loaded_functions, search_string, max_sites=10):
    total_len_database = 0
    site_count = 0

    for module_alias, (search_function, use_for) in loaded_functions.items():
        if max_sites is not None and site_count >= max_sites:
            break

        console.print(f"\n[blue]Searching in module: {module_alias} [white](Use for: {use_for})")
        
        try:
            database: MediaManager = search_function(search_string, get_onylDatabase=True)
            len_database = len(database.media_list)

            for element in database.media_list:
                print(element.__dict__)

            console.print(f"[green]Database length for {module_alias}: {len_database}")
            total_len_database += len_database 
            site_count += 1 

        except Exception as e:
            console.print(f"[red]Error while executing search function for {module_alias}: {str(e)}")

    return total_len_database


# Main
search_string = "cars"
loaded_functions = load_search_functions()

total_len = search_all_sites(loaded_functions, search_string)
console.print(f"\n[cyan]Total number of results from all sites: {total_len}")
