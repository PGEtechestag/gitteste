@echo off
chcp 65001 >nul
title Paritarios SPPrev - Consulta e Gerenciamento
cd /d "%~dp0"

echo ========================================
echo  Paritarios SPPrev
echo ========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Instale o Python em https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

python main.py
if errorlevel 1 (
    echo.
    echo Ocorreu um erro ao executar o aplicativo.
    pause
)
