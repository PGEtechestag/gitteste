@echo off
chcp 65001 >nul
title Paritarios SPPrev - Gerar Executavel
echo ========================================
echo  Paritarios SPPrev - Build
echo ========================================
echo.

REM Verifica se PyInstaller esta instalado
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo PyInstaller nao encontrado. Instalando...
    pip install pyinstaller
)

echo Gerando executavel...
echo.

REM Executa o build
pyinstaller build.spec --clean --noconfirm

echo.
if exist "dist\ParitariosSPPrev.exe" (
    echo ========================================
    echo  Build concluido com sucesso!
    echo ========================================
    echo.
    echo Executavel gerado em: dist\ParitariosSPPrev.exe
    echo.
    echo Para distribuir, basta copiar a pasta 'dist' para outro PC.
    echo.
) else (
    echo ERRO: Falha ao gerar executavel.
)

pause