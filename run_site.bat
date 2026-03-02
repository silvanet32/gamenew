@echo off
setlocal

echo ====================================
echo GameNew - Setup + Build + Start
echo ====================================

call install_deps.bat
if errorlevel 1 (
  echo Nao foi possivel concluir instalacao de dependencias.
  pause
  exit /b 1
)

call build_frontend.bat
if errorlevel 1 (
  echo AVISO: Build do frontend falhou. O backend ainda pode iniciar.
)

call start_site.bat
exit /b %errorlevel%
