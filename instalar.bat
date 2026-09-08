@echo off
chcp 65001 >nul
title Paritarios SPPrev - Instalacao de Dependencias
echo ========================================
echo  Paritarios SPPrev - Instalacao
echo ========================================
echo.

REM Verifica se Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo.
    echo Por favor, instale o Python 3.9 ou superior em:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANTE: Durante a instalacao, marque a opcao "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo [1/2] Python encontrado!
echo.

REM Verifica se pip esta atualizado
echo [2/2] Atualizando pip...
python -m pip install --upgrade pip
echo.

REM Instala dependencias
echo Instalando dependencias...
echo.
pip install -r requirements.txt

echo.
echo ========================================
echo  Instalacao concluida!
echo ========================================
echo.
echo Para executar o aplicativo, use: python main.py
echo.
pause