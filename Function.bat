@echo off

:: set path 
set ROOT=%~dp0
set PYTHONPATH=%ROOT%\\.venv\\Scripts\\python.exe
set RUNNER=vta.core.runner.function

:: set args
set TASK=hello.robot
set SLOT=1

:: run 
%PYTHONPATH% -m %RUNNER% --task %TASK% --slot %SLOT%