# 21.06.24

import os
import inspect


def get_call_stack():
    """
    Retrieves the current call stack with details about each call.

    This function inspects the current call stack and returns a list of dictionaries,
    where each dictionary contains details about a function call in the stack.

    Returns:
        list: A list of dictionaries, each containing the following keys:
            - function (str): The name of the function.
            - folder (str): The directory path of the script containing the function.
            - script (str): The name of the script file containing the function.
            - line (int): The line number in the script where the function is defined.

    Example:
        >>> def func_a():
        ...     return func_b()
        ...
        >>> def func_b():
        ...     return func_c()
        ...
        >>> def func_c():
        ...     return get_call_stack()
        ...
        >>> stack_trace = func_a()
        >>> for frame in stack_trace:
        ...     print(f"Function: {frame['function']}, Folder: {frame['folder']}, "
        ...           f"Script: {frame['script']}, Line: {frame['line']}")
    """
    stack = inspect.stack()
    call_stack = []

    for frame_info in stack:
        function_name = frame_info.function
        filename = frame_info.filename
        lineno = frame_info.lineno
        folder_name = os.path.dirname(filename)
        script_name = os.path.basename(filename)

        call_stack.append({
            "function": function_name,
            "folder": folder_name,
            "script": script_name,
            "line": lineno
        })
        
    return call_stack
