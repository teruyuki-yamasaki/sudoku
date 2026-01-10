@echo off
REM ============================================
REM activate_venv.bat
REM Python 仮想環境 "sra" を有効化するスクリプト
REM ============================================

REM ---- ユーザーのホームディレクトリ ----
set "WORK_DIR=C:\Users\%USERNAME%\work"

REM ---- 仮想環境設定 ----
set "VENV_NAME=sdk"
set "VENV_PATH=%WORK_DIR%\.venvs\%VENV_NAME%"

REM ---- 仮想環境の存在確認 ----
if not exist "%VENV_PATH%\Scripts\activate.bat" (
    echo [ERROR] 仮想環境 "%VENV_NAME%" が見つかりません。
    echo Path: %VENV_PATH%
    pause
    exit /b 1
)

REM ---- 仮想環境を有効化 ----
call "%VENV_PATH%\Scripts\activate.bat"

REM ---- シェルを開いたままにする ----
cmd /k
