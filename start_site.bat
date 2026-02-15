@echo off
setlocal

echo ====================================
echo GameNew - Iniciar Site
echo ====================================

if not exist ".venv\Scripts\activate.bat" (
  echo ERRO: .venv nao encontrada.
  echo Rode primeiro: install_deps.bat
  pause
  exit /b 1
)

echo Iniciando Backend Flask em nova janela...
start "GameNew Backend" cmd /k "cd /d %cd% && call .venv\Scripts\activate.bat && python app.py"

echo Iniciando Frontend Vite em nova janela...
where npm >nul 2>nul
if errorlevel 1 (
  echo AVISO: npm nao encontrado, frontend nao iniciado.
) else (
  start "GameNew Frontend" cmd /k "cd /d %cd%\frontend && npm run dev"
)

echo.
echo Backend:  http://127.0.0.1:5000
echo Frontend: http://127.0.0.1:5173
pause
exit /b 0
