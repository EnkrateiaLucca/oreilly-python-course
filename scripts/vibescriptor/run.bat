@echo off
REM Launcher script for Vibescriptor (Windows)

REM Check if API key is set
if "%OPENAI_API_KEY%"=="" if "%ANTHROPIC_API_KEY%"=="" (
    echo ❌ Error: No API key found!
    echo.
    echo Please set one of these environment variables:
    echo   set OPENAI_API_KEY=your-key
    echo   set ANTHROPIC_API_KEY=your-key
    echo.
    exit /b 1
)

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

REM Navigate to project root (two levels up from scripts\vibescriptor)
cd /d "%SCRIPT_DIR%..\.."

REM Run vibescriptor
uv run python scripts\vibescriptor\vibescriptor.py
