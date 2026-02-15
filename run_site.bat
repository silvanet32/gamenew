@echo off
setlocal

echo ====================================
echo GameNew - Setup + Start (Windows)
echo ====================================

call install_deps.bat
if errorlevel 1 (
  echo Nao foi possivel concluir a instalacao de dependencias.
  pause
  exit /b 1
)

call start_site.bat
exit /b %errorlevel%
