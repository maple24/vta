@echo off

:: set path 
set ROOT=%~dp0
set PYTHONPATH=%ROOT%\\.venv\\Scripts\\python.exe
set RUNNER=%ROOT%\\vat\\core\\Runner\\helloworld.py

:: run 
%PYTHONPATH% %RUNNER%