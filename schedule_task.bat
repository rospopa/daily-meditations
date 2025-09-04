@echo off
echo Creating Windows Task Scheduler task to run daily meditation emailer...

REM Get the current directory
set SCRIPT_DIR=%~dp0
set SCRIPT_PATH=%SCRIPT_DIR%daily_meditation.py

REM Create the task
schtasks /create /tn "Daily Meditation Emailer" /tr "python \"%SCRIPT_PATH%\"" /sc daily /st 07:00 /f

if %ERRORLEVEL% EQU 0 (
    echo Task created successfully! The script will run daily at 7:00 AM.
    echo You can modify this schedule in Windows Task Scheduler.
) else (
    echo Failed to create the task. Please try running this script as administrator.
)

pause
