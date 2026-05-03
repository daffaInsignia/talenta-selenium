@echo off
:: Setup Windows Task Scheduler for Talenta Auto Attendance
:: Run this script as Administrator

set "RUN_BAT=%~dp0run.bat"

echo ============================================
echo  Talenta Auto Attendance - Task Scheduler
echo ============================================
echo.
echo Script: %RUN_BAT%
echo.

:: Delete existing tasks if any
schtasks /delete /tn "TalentaClockIn" /f >nul 2>&1
schtasks /delete /tn "TalentaClockOut" /f >nul 2>&1
schtasks /delete /tn "TalentaClockInStartup" /f >nul 2>&1
schtasks /delete /tn "TalentaAttendance" /f >nul 2>&1

:: Every 15 minutes, check and clock in/out if needed (interactive so Chrome can start)
schtasks /create /tn "TalentaAttendance" /tr "\"%RUN_BAT%\"" /sc minute /mo 15 /rl highest /it /f
echo [OK] TalentaAttendance scheduled every 15 minutes

:: At logon, immediately check
schtasks /create /tn "TalentaClockInStartup" /tr "\"%RUN_BAT%\"" /sc onlogon /rl highest /it /f
echo [OK] TalentaClockInStartup scheduled at logon

echo.
echo ============================================
echo  Done! Scheduled tasks:
echo   - TalentaAttendance    : every 15 minutes
echo   - TalentaClockInStartup: at logon
echo ============================================
echo.
echo To verify: schtasks /query /tn "TalentaAttendance"
echo To remove:
echo   schtasks /delete /tn "TalentaAttendance" /f
echo   schtasks /delete /tn "TalentaClockInStartup" /f
echo.
pause
