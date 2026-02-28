@echo off
REM Install required packages
echo Installing required packages...
pip install -r requirements.txt

REM Run the application
echo Starting MP3 Metadata Editor...
python mp3_metadata_editor.py

pause
