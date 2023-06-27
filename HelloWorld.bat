@echo off

:: set path 
set ROOT=%~dp0
set PYTHONPATH=%ROOT%\\.venv\\Scripts\\python.exe
set RUNNER=%ROOT%\\vat\\core\\Runner\\stability.py

:: set args
set TASK=hello.robot
set SLOT=1
set MAXLOOP=10

:: run 
%PYTHONPATH% %RUNNER% --task %TASK% --slot %SLOT% --max_loop %MAXLOOP%