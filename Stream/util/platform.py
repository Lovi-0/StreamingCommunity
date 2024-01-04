import platform

def is_platform_windows():
    return platform.system() == "Windows"

def is_platform_linux():
    return platform.system() == "Linux"
