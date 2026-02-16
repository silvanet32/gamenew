@echo off
setlocal

echo ====================================
echo GameNew - Iniciar Site (URL unica)
echo ====================================

if not exist ".venv\Scripts\activate.bat" (
  echo ERRO: .venv nao encontrada.
  echo Rode primeiro: install_deps.bat
  pause
  exit /b 1
)

echo Iniciando servidor Flask (backend + frontend na mesma URL)...
start "GameNew (Flask + Front integrado)" cmd /k "cd /d %cd% && call .venv\Scripts\activate.bat && python app.py"

echo.
echo Use UMA URL principal:
echo - http://127.0.0.1:5000/app  (frontend integrado)
echo - APIs e backend na mesma origem

echo.
echo Se o /app mostrar aviso, rode antes: build_frontend.bat
pause
exit /b 0
