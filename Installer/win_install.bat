@echo off

:: Spostarsi nella directory superiore rispetto a quella corrente
cd ..

:: Check if the script is running as administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Running as administrator...
    :: Restart the script with administrator privileges
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

chcp 65001 > nul
SETLOCAL ENABLEDELAYEDEXPANSION

echo Script starting...

:: Check if Chocolatey is already installed
:check_choco
echo Checking if Chocolatey is installed...
choco --version >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    echo Chocolatey is already installed. Skipping installation.
    goto install_python
) ELSE (
    echo Installing Chocolatey...
    @"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))" || (
        echo Error during Chocolatey installation.
        exit /b 1
    )
    echo Chocolatey installed successfully.
    call choco --version
    echo.
)

:: Check if Python is already installed
:install_python
echo Checking if Python is installed...
python -V >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    echo Python is already installed. Skipping installation.
    goto install_openssl
) ELSE (
    echo Installing Python...
    choco install python --confirm --params="'/NoStore'" --allow-downgrade || (
        echo Error during Python installation.
        exit /b 1
    )
    echo Python installed successfully.
    call python -V
    echo.
)

:: Ask to restart the terminal
echo Please restart the terminal to continue...
pause
exit /b

:: Check if OpenSSL is already installed
:install_openssl
echo Checking if OpenSSL is installed...
openssl version -a >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    echo OpenSSL is already installed. Skipping installation.
    goto install_ffmpeg
) ELSE (
    echo Installing OpenSSL...
    choco install openssl --confirm || (
        echo Error during OpenSSL installation.
        exit /b 1
    )
    echo OpenSSL installed successfully.
    call openssl version -a
    echo.
)

:: Check if FFmpeg is already installed
:install_ffmpeg
echo Checking if FFmpeg is installed...
ffmpeg -version >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    echo FFmpeg is already installed. Skipping installation.
    goto create_venv
) ELSE (
    echo Installing FFmpeg...
    choco install ffmpeg --confirm || (
        echo Error during FFmpeg installation.
        exit /b 1
    )
    echo FFmpeg installed successfully.
    call ffmpeg -version
    echo.
)

:: Verify installations
:verifica_installazioni
echo Verifying installations...
call choco --version
call python -V
call openssl version -a
call ffmpeg -version

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
        exit /b 1
    )
    echo Virtual environment created successfully.
)

:: Activate the virtual environment and install requirements
echo Installing requirements...
call .venv\Scripts\activate.bat
pip install -r requirements.txt || (
    echo Error during requirements installation.
    exit /b 1
)

:: Run run.py
echo Running test_run.py...
call .venv\Scripts\python .\test_run.py || (
    echo Error during run.py execution.
    exit /b 1
)

echo End of script.

ENDLOCAL
