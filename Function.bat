@echo off

:: set path 
set ROOT=%~dp0
set PYTHONPATH=%ROOT%\\.venv\\Scripts\\python.exe
set RUNNER=%ROOT%\\vta\\core\\runner\\function.py

:: set args
set TASK=hello.robot
set SLOT=1

:: run 
%PYTHONPATH% %RUNNER% --task %TASK% --slot %SLOT%