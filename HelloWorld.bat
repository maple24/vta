@echo off

:: set path 
set ROOT=%~dp0
set PYTHONPATH=%ROOT%\\.venv\\Scripts\\python.exe
set RUNNER=%ROOT%\\scripts\\Runners\\HelloWorld.py

:: run 
%PYTHONPATH% %RUNNER%