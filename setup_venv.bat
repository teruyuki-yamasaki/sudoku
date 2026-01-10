@echo off
REM ============================================
REM setup_venv.bat
REM Python 仮想環境 "foo" を作成するスクリプト
REM ============================================

REM ---- 作業ディレクトリ ----
set WORK_DIR=C:\Users\%USERNAME%\work\

REM ---- 仮想環境名 ----
set VENV_NAME=sdk
set VENV_BASE=%WORK_DIR%\.venvs
set VENV_PATH=%VENV_BASE%\%VENV_NAME%

REM ---- Python 実行ファイル確認 ----
where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python が見つかりません。PATH を確認してください。
    pause
    exit /b 1
)

REM ---- .venvs ディレクトリ作成 ----
if not exist "%VENV_BASE%" (
    echo Creating directory: %VENV_BASE%
    mkdir "%VENV_BASE%"
)

REM ---- 仮想環境が既に存在するか確認 ----
if exist "%VENV_PATH%\Scripts\activate.bat" (
    echo [INFO] 仮想環境 "%VENV_NAME%" は既に存在します。
    echo Path: %VENV_PATH%
    pause
    exit /b 0
)

REM ---- 仮想環境作成 ----
echo Creating virtual environment: %VENV_NAME%
python -m venv "%VENV_PATH%"

if errorlevel 1 (
    echo [ERROR] 仮想環境の作成に失敗しました。
    pause
    exit /b 1
)

REM ---- pip 更新（任意だが推奨）----
call "%VENV_PATH%\Scripts\activate.bat"
python -m pip install --upgrade pip
deactivate

echo.
echo [SUCCESS] 仮想環境 "%VENV_NAME%" を作成しました。
echo 有効化するには activate_venv.bat を実行してください。
pause
