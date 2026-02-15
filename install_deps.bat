@echo off
setlocal

echo ====================================
echo GameNew - Instalar Dependencias
echo ====================================

echo [1/4] Verificando Python...
where python >nul 2>nul
if errorlevel 1 (
  echo ERRO: Python nao encontrado no PATH.
  echo Instale Python 3.10+ e marque "Add Python to PATH".
  goto :end_fail
)

echo [2/4] Criando/ativando .venv...
if not exist ".venv" (
  python -m venv .venv
  if errorlevel 1 (
    echo ERRO: Nao foi possivel criar .venv.
    goto :end_fail
  )
)
call ".venv\Scripts\activate.bat"
if errorlevel 1 (
  echo ERRO: Nao foi possivel ativar .venv.
  goto :end_fail
)

echo [3/4] Instalando backend (Python)...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
  echo AVISO: Falha ao instalar dependencias Python.
  echo Continue para tentar instalar frontend.
)

echo [4/4] Instalando frontend (Node)...
where npm >nul 2>nul
if errorlevel 1 (
  echo AVISO: npm nao encontrado. Instale Node.js 18+.
  goto :end_ok
)

if not exist "frontend\package.json" (
  echo AVISO: frontend\package.json nao encontrado.
  goto :end_ok
)

pushd frontend
call npm install
if errorlevel 1 (
  echo AVISO: Falha no npm install. Verifique internet/proxy.
)
popd

goto :end_ok

:end_fail
echo.
echo Processo finalizado com erro.
pause
exit /b 1

:end_ok
echo.
echo Dependencias processadas.
pause
exit /b 0
