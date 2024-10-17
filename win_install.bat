@echo off
:: Controlla se lo script è in esecuzione come amministratore
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Eseguendo come amministratore...
    :: Riavvia lo script con privilegi di amministratore
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

chcp 65001 > nul
SETLOCAL ENABLEDELAYEDEXPANSION

echo Inizio dello script...

:: Controlla se Chocolatey è già installato
:check_choco
echo Verifica se Chocolatey è installato...
choco --version >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    echo Chocolatey è già installato. Salto l'installazione.
    goto install_python
) ELSE (
    echo Installazione di Chocolatey...
    @"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))" || (
        echo Errore durante l'installazione di Chocolatey.
        exit /b 1
    )
    echo Chocolatey installato con successo.
    call choco --version
    echo.
)

:: Controlla se Python è già installato
:install_python
echo Verifica se Python è installato...
python -V >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    echo Python è già installato. Salto l'installazione.
    goto install_openssl
) ELSE (
    echo Installazione di Python...
    choco install python --confirm --params="'/NoStore'" --allow-downgrade || (
        echo Errore durante l'installazione di Python.
        exit /b 1
    )
    echo Python installato con successo.
    call python -V
    echo.
)

:: Chiedi di riavviare il terminale
echo Si prega di riavviare il terminale per continuare...
pause
exit /b

:: Controlla se OpenSSL è già installato
:install_openssl
echo Verifica se OpenSSL è installato...
openssl version -a >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    echo OpenSSL è già installato. Salto l'installazione.
    goto install_ffmpeg
) ELSE (
    echo Installazione di OpenSSL...
    choco install openssl --confirm || (
        echo Errore durante l'installazione di OpenSSL.
        exit /b 1
    )
    echo OpenSSL installato con successo.
    call openssl version -a
    echo.
)

:: Controlla se FFmpeg è già installato
:install_ffmpeg
echo Verifica se FFmpeg è installato...
ffmpeg -version >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    echo FFmpeg è già installato. Salto l'installazione.
    goto create_venv
) ELSE (
    echo Installazione di FFmpeg...
    choco install ffmpeg --confirm || (
        echo Errore durante l'installazione di FFmpeg.
        exit /b 1
    )
    echo FFmpeg installato con successo.
    call ffmpeg -version
    echo.
)

:: Verifica delle installazioni
:verifica_installazioni
echo Verifica delle installazioni...
call choco --version
call python -V
call openssl version -a
call ffmpeg -version

echo Tutti i programmi sono stati installati e verificati con successo.

:: Crea un ambiente virtuale .venv
:create_venv
echo Verifica se l'ambiente virtuale .venv esiste già...
if exist .venv (
    echo L'ambiente virtuale .venv esiste già. Salto la creazione.
) ELSE (
    echo Creazione dell'ambiente virtuale .venv...
    python -m venv .venv || (
        echo Errore durante la creazione dell'ambiente virtuale.
        exit /b 1
    )
    echo Ambiente virtuale creato con successo.
)

:: Attiva l'ambiente virtuale e installa i requisiti
echo Installazione dei requisiti...
call .venv\Scripts\activate.bat
pip install -r requirements.txt || (
    echo Errore durante l'installazione dei requisiti.
    exit /b 1
)

:: Esegui run.py
echo Esecuzione di run.py...
call .venv\Scripts\python .\run.py || (
    echo Errore durante l'esecuzione di run.py.
    exit /b 1
)

echo Fine dello script.

ENDLOCAL
