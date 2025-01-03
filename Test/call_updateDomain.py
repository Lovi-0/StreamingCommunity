# 12.11.24

# Fix import
import os
import sys
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(src_path)


# Other
import time
import glob
import logging
import importlib
from rich.console import Console


# Util
from StreamingCommunity.Util._jsonConfig import config_manager
from StreamingCommunity.Api.Template.Util import search_domain


# Variable
console = Console()
README_PATH = "README.md"


def load_site_names():
    modules = []
    site_names = {}

    # Traverse the Api directory
    api_dir = os.path.join(os.path.dirname(__file__), '..', 'StreamingCommunity', 'Api', 'Site')
    init_files = glob.glob(os.path.join(api_dir, '*', '__init__.py'))

    # Retrieve modules and their indices
    for init_file in init_files:

        # Get folder name as module name
        module_name = os.path.basename(os.path.dirname(init_file))
        logging.info(f"Load module name: {module_name}")

        try:
            # Dynamically import the module
            mod = importlib.import_module(f'StreamingCommunity.Api.Site.{module_name}')

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

    # Load SITE_NAME from each module in the sorted order
    for module_name, _, use_for in modules:

        # Construct a unique alias for the module
        module_alias = f'{module_name}'
        logging.info(f"Module alias: {module_alias}")

        try:
            # Dynamically import the module
            mod = importlib.import_module(f'StreamingCommunity.Api.Site.{module_name}')

            # Get the SITE_NAME variable from the module
            site_name = getattr(mod, 'SITE_NAME', None)

            if site_name:
                # Add the SITE_NAME to the dictionary
                site_names[module_alias] = (site_name, use_for)

        except Exception as e:
            console.print(f"[red]Failed to load SITE_NAME from module {module_name}: {str(e)}")

    return site_names

def update_readme(site_names, domain_to_use):
    if not os.path.exists(README_PATH):
        console.print(f"[red]README file not found at {README_PATH}")
        return

    with open(README_PATH, "r", encoding="utf-8") as file:
        lines = file.readlines()

    updated_lines = []

    for line in lines:
        if line.startswith("| [") and "|" in line:
            site_name = line.split("[")[1].split("]")[0]
            alias = f"{site_name.lower()}"

            if alias in site_names:
                print("Update line: ", line)
                
                if site_name == "animeunity":
                    updated_line = f"| [{site_name}](https://www.{alias}.{domain_to_use}/) |   ✅   |\n"
                else:
                    updated_line = f"| [{site_name}](https://{alias}.{domain_to_use}/) |   ✅   |\n"

                print("To: ", updated_line.strip())
                updated_lines.append(updated_line)
                continue

        updated_lines.append(line)

    with open(README_PATH, "w", encoding="utf-8") as file:
        file.writelines(updated_lines)

if __name__ == "__main__":
    site_names = load_site_names()
    for alias, (site_name, use_for) in site_names.items():
        original_domain = config_manager.get_list("SITE", alias)['domain']

        if site_name == "animeunity":
            domain_to_use, _ = search_domain(site_name=site_name, base_url=f"https://www.{site_name}", get_first=True)
        else:
            domain_to_use, _ = search_domain(site_name=site_name, base_url=f"https://{site_name}", get_first=True)
            
        # Update readme
        if original_domain != domain_to_use:
            print("\n")
            print("Return domain: ", domain_to_use)
            update_readme(alias, domain_to_use)
            
        print("------------------------------------")
        time.sleep(2)