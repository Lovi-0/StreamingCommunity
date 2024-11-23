# 19.10.24

import os
import sys

def execute_search(info):
    """
    Dynamically imports and executes a specified function from a module defined in the info dictionary.

    Parameters:
        info (dict): A dictionary containing the function name, folder, and module information.
    """

    # Define the project path using the folder from the info dictionary
    project_path = os.path.dirname(info['folder'])  # Get the base path for the project

    # Add the project path to sys.path
    if project_path not in sys.path:
        sys.path.append(project_path)

    # Attempt to import the specified function from the module
    try:
        # Construct the import statement dynamically
        module_path = f"StreamingCommunity.Src.Api.Site{info['folder_base']}"
        exec(f"from {module_path} import {info['function']}")

        # Call the specified function
        eval(info['function'])()  # Calls the search function

    except ModuleNotFoundError as e:
        print(f"ModuleNotFoundError: {e}")

    except ImportError as e:
        print(f"ImportError: {e}")

    except Exception as e:
        print(f"An error occurred: {e}")
