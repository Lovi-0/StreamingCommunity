@echo off

:: Check if the script is running as administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Running as administrator...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

chcp 65001 > nul
SETLOCAL ENABLEDELAYEDEXPANSION

echo Script starting...

:: Check if PowerShell is available
where powershell >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo PowerShell is not available on this system. Please ensure it is installed and configured.
    echo Press any key to close...
    pause >nul
    exit /b 1
)

:: Check if Chocolatey is already installed
:check_choco
echo Checking if Chocolatey is installed...
choco --version >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    echo Chocolatey is already installed. Skipping installation.
    goto install_python
) ELSE (
    echo Installing Chocolatey...
    @"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -ExecutionPolicy Bypass -Command "[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))" || (
        echo Error during Chocolatey installation.
        echo Press any key to close...
        pause >nul
        exit /b 1
    )
    echo Chocolatey installed successfully.
    where choco >nul 2>&1 || (
        echo Chocolatey is not recognized. Ensure it is correctly installed and PATH is configured.
        echo Press any key to close...
        pause >nul
        exit /b 1
    )
)

:: Check if Python is already installed
:install_python
echo Checking if Python is installed...
python -V >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    echo Python is already installed. Skipping installation.
) ELSE (
    echo Installing Python...
    choco install python --confirm --params="'/NoStore'" --allow-downgrade || (
        echo Error during Python installation.
        echo Press any key to close...
        pause >nul
        exit /b 1
    )
    echo Python installed successfully.
    call python -V
    echo.
    echo Please restart the terminal to continue...
    pause >nul
    exit /b
)

:: Verify installations
:verifica_installazioni
echo Verifying installations...
call choco --version
call python -V

echo All programs have been successfully installed and verified.

:: Create a virtual environment .venv
:create_venv
echo Checking if the .venv virtual environment already exists...
if exist .venv (
    echo The .venv virtual environment already exists. Skipping creation.
) ELSE (
    echo Creating the .venv virtual environment...
    python -m venv .venv || (
        echo Error during virtual environment creation.
        echo Press any key to close...
        pause >nul
        exit /b 1
    )
    echo Virtual environment created successfully.
)

:: Activate the virtual environment and install requirements
echo Installing requirements...
echo Current directory: %CD%
call .venv\Scripts\activate.bat
pip install -r requirements.txt || (
    echo Error during requirements installation.
    echo Press any key to close...
    pause >nul
    exit /b 1
)

:: Run test_run.py
echo Running test_run.py...
call .venv\Scripts\python .\test_run.py || (
    echo Error during test_run.py execution.
    echo Press any key to close...
    pause >nul
    exit /b 1
)

echo End of script.

echo Press any key to close...
pause >nul

ENDLOCAL