@echo off
setlocal

where npm >nul 2>nul
if errorlevel 1 (
  echo ERRO: npm nao encontrado. Instale Node.js 18+.
  pause
  exit /b 1
)

if not exist "frontend\package.json" (
  echo ERRO: frontend\package.json nao encontrado.
  pause
  exit /b 1
)

pushd frontend
call npm run build
if errorlevel 1 (
  echo ERRO: Falha no build do frontend.
  popd
  pause
  exit /b 1
)
popd

echo Build concluido em frontend\dist
pause
exit /b 0
