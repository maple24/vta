@echo off

:: set path 
cd ..\..
set ROOT=%CD%
set PYTHONPATH=%ROOT%\\.venv\\Scripts\\python.exe
set ROBOTPATH=%ROOT%\\.venv\\Scripts\\robot.exe
set SCRIPTPATH=%ROOT%\\vat\\tasks\\hello.robot
set LOGPATH=%ROOT%\\log
%PYTHONPATH% --version

:: run scripts
%ROBOTPATH% --timestampoutputs --outputdir %LOGPATH% %SCRIPTPATH%
pause
