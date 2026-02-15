@echo off
setlocal enabledelayedexpansion

REM =============================
REM GameNew - Setup + Run (Windows)
REM =============================

echo [1/5] Verificando Python...
where python >nul 2>nul
if errorlevel 1 (
  echo ERRO: Python nao encontrado no PATH.
  echo Instale Python 3.10+ e marque "Add Python to PATH".
  pause
  exit /b 1
)

echo [2/5] Criando/ativando ambiente virtual (.venv)...
if not exist .venv (
  python -m venv .venv
  if errorlevel 1 (
    echo ERRO: Falha ao criar ambiente virtual.
    pause
    exit /b 1
  )
)

call .venv\Scripts\activate.bat
if errorlevel 1 (
  echo ERRO: Falha ao ativar .venv.
  pause
  exit /b 1
)

echo [3/5] Instalando dependencias do backend (Flask)...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
  echo AVISO: Falha ao instalar dependencias Python.
  echo Verifique internet/proxy e execute novamente.
)

echo [4/5] Instalando dependencias do frontend (React + Vite)...
where npm >nul 2>nul
if errorlevel 1 (
  echo AVISO: npm nao encontrado. Instale Node.js 18+ para rodar frontend.
) else (
  pushd frontend
  npm install
  if errorlevel 1 (
    echo AVISO: Falha ao instalar dependencias do frontend.
    echo Verifique internet/proxy e execute novamente.
  )
  popd
)

echo [5/5] Iniciando servicos...
echo - Backend Flask: http://127.0.0.1:5000
echo - Frontend Vite: http://127.0.0.1:5173

start "GameNew Backend" cmd /k "call .venv\Scripts\activate.bat && python app.py"

where npm >nul 2>nul
if errorlevel 1 (
  echo Frontend nao iniciado porque npm nao foi encontrado.
) else (
  start "GameNew Frontend" cmd /k "cd /d %cd%\frontend && npm run dev"
)

echo.
echo Pronto! Pressione qualquer tecla para sair desta janela.
pause >nul
exit /b 0
