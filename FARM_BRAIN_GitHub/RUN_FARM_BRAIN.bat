@echo off
setlocal
cd /d "%~dp0"
echo.
echo ==========================================
echo        FARM BRAIN - WEBSITE STARTER
echo ==========================================
echo.
where py >nul 2>nul
if errorlevel 1 (
  echo Python launcher was not found. Install Python 3.12 from python.org and select Add Python to PATH.
  pause
  exit /b 1
)
py -3.12 --version >nul 2>nul
if errorlevel 1 (
  echo Python 3.12 was not found. Install Python 3.12 from https://www.python.org/downloads/
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
  echo Creating the Python 3.12 environment...
  py -3.12 -m venv .venv
  if errorlevel 1 goto failed
)
call ".venv\Scripts\activate.bat"
if not exist ".env" copy ".env.example" ".env" >nul
echo Installing required packages (first run needs internet)...
python -m pip install --upgrade pip
if errorlevel 1 goto failed
pip install -r requirements.txt
if errorlevel 1 goto failed
echo.
echo Starting FARM BRAIN. Keep this window open while using the website.
echo Open http://127.0.0.1:5000 in your browser.
echo Stop the website by pressing Ctrl+C in this window.
echo.
python run.py
if errorlevel 1 goto failed
exit /b 0
:failed
echo.
echo Setup did not complete. Read README.md and check the error above.
pause
exit /b 1
