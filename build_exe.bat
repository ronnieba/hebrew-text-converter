@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Creating EXE file...
pyinstaller --onefile --windowed --name="HebrewConverter" --icon=icon.ico hebrew_converter_tray.py

echo.
echo Done! The EXE file is in the 'dist' folder.
pause
