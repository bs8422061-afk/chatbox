@echo off
REM CuriBot launcher - rebuilds the virtual environment for THIS folder and starts the app.
cd /d "%~dp0"

REM The old .venv was created at H:\project\Curibot and has no Flask - rebuild it once here.
if not exist ".venv\curibot_ready.txt" (
    echo Setting up Python environment, please wait...
    if exist ".venv" rmdir /s /q ".venv"
    py -3 -m venv .venv 2>nul || python -m venv .venv
    if not exist ".venv\Scripts\python.exe" (
        echo Could not create the virtual environment. Is Python installed?
        pause
        exit /b 1
    )
    ".venv\Scripts\python.exe" -m pip install --upgrade pip
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Failed to install Flask. Check your internet connection.
        pause
        exit /b 1
    )
    echo ready> ".venv\curibot_ready.txt"
)

echo.
echo CuriBot is starting... open http://127.0.0.1:5000 in your browser
echo Press Ctrl+C to stop.
echo.
start "" http://127.0.0.1:5000
".venv\Scripts\python.exe" app.py
pause
