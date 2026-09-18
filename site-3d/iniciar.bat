@echo off
REM ============================================================
REM  Guardanapeiro Modular - configurador 3D (Windows)
REM  Copia os STL, instala dependencias e sobe o servidor local.
REM ============================================================
title Guardanapeiro Modular - Servidor 3D
cd /d "%~dp0"

set ORIGEM=C:\Users\eletrica2\Desktop\Projetos Henri\Site modelo 3d\Modelos
set DESTINO=%~dp0public\modelos

echo.
echo [1/3] Copiando arquivos .STL...
if not exist "%DESTINO%" mkdir "%DESTINO%"
if exist "%ORIGEM%" (
    xcopy "%ORIGEM%\*.stl" "%DESTINO%\" /Y /I >nul
    echo      STL copiados de: %ORIGEM%
) else (
    echo      [aviso] Pasta de origem nao encontrada. Usando os STL que ja estao em public\modelos.
)

echo.
echo [2/3] Instalando dependencias (npm install)...
call npm install --no-fund --no-audit
if errorlevel 1 (
    echo      [erro] Falha no npm install. O Node.js esta instalado? https://nodejs.org
    pause
    exit /b 1
)

echo.
echo [3/3] Subindo o servidor em http://localhost:3000
start "" http://localhost:3000
call npm start
pause
