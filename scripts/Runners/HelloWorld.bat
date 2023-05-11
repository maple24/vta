@echo off

:: set path 
cd ..\..
set ROOT=%CD%
set PYTHONPATH=%ROOT%\\.venv\\Scripts\\python.exe
set ROBOTPATH=%ROOT%\\.venv\\Scripts\\robot.exe
set DATE=%date: =_%
set DATE=%DATE:/=%
set LOGPATH=%ROOT%\\log

SET SLOTID=1
set SCRIPTPATH=%ROOT%\\vat\\tasks\\hello.robot

:: run scripts
%ROBOTPATH% --timestampoutputs --outputdir %LOGPATH%\\%DATE%_SLOT%SLOTID% --report NONE %SCRIPTPATH%
pause