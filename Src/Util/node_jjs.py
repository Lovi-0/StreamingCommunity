# 26.05.24

import subprocess

def is_node_installed() -> bool:
    """
    Checks if Node.js is installed on the system.

    Returns:
        bool: True if Node.js is installed, False otherwise.
    """
    try:
        # Run the command 'node -v' to get the Node.js version
        result = subprocess.run(['node', '-v'], capture_output=True, text=True, check=True)

        # If the command runs successfully and returns a version number, Node.js is installed
        if result.stdout.startswith('v'):
            return True
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        # If there is an error running the command or the command is not found, Node.js is not installed
        return False

    return False

def run_node_script(script_content: str) -> str:
    """
    Runs a Node.js script and returns its output.

    Args:
        script_content (str): The content of the Node.js script to run.

    Returns:
        str: The output of the Node.js script.
    """

    # Check if Node.js is installed
    if not is_node_installed():
        raise EnvironmentError("Node.js is not installed on the system.")

    # Write the script content to a temporary file
    with open('script.js', 'w') as file:
        file.write(script_content)

    try:
        # Run the Node.js script using subprocess and capture the output
        result = subprocess.run(['node', 'script.js'], capture_output=True, text=True, check=True)
        return result.stdout
    
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error running Node.js script: {e.stderr}")
    
    finally:
        # Clean up the temporary script file
        import os
        os.remove('script.js')
