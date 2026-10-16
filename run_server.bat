@echo off
cd /d "%~dp0"
echo ========================================================
echo   MISS SUNFLOWER CAMBODIA - FULL-STACK LOCALHOST SERVER
echo   Frontend : http://localhost:8000/
echo   Admin CMS: http://localhost:8000/admin.html
echo   REST API : http://localhost:8000/api/settings
echo ========================================================
echo Starting server...
if exist ".py_runtime\python.exe" (
    ".py_runtime\python.exe" start_server.py
) else if exist ".py_runtime\py.exe" (
    ".py_runtime\py.exe" start_server.py
) else (
    python start_server.py
)
pause
