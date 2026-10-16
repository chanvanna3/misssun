@echo off
chcp 65001 >nul
title Miss Sunflower FastAPI Server

echo ======================================================================
echo    🌻 Miss Sunflower FastAPI Enterprise Server
echo ======================================================================
echo.

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

if exist "%SCRIPT_DIR%.py_runtime\python.exe" (
    set "PYTHON_EXE=%SCRIPT_DIR%.py_runtime\python.exe"
) else (
    set "PYTHON_EXE=python"
)

echo Starting FastAPI server with Uvicorn...
"%PYTHON_EXE%" fastapi_server.py 8000

pause
