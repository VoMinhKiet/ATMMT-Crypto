@echo off
rem Dong goi ung dung thanh mot file Nhom17-Crypto.exe (nam ngay trong thu muc nay).
rem Can: pip install customtkinter pyinstaller
cd /d "%~dp0"
python -m PyInstaller --noconfirm --clean --onefile --windowed ^
  --name Nhom17-Crypto ^
  --icon "%~dp0assets\icon.ico" ^
  --add-data "%~dp0assets\icon.ico;assets" ^
  --collect-data customtkinter ^
  --exclude-module numpy ^
  --exclude-module Crypto ^
  --exclude-module pymupdf ^
  --exclude-module fitz ^
  --exclude-module pypdf ^
  --exclude-module onnxruntime ^
  --distpath "%~dp0." ^
  --workpath "%~dp0build" ^
  --specpath "%~dp0build" ^
  main.py
if errorlevel 1 (
  echo.
  echo Dong goi THAT BAI.
  exit /b 1
)
rmdir /s /q "%~dp0build"
echo.
echo Xong: %~dp0Nhom17-Crypto.exe
