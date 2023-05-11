@echo off

:: set path 
cd ..\..
set ROOT=%CD%
set REBOTPATH=%ROOT%\\.venv\\Scripts\\rebot.exe
set DATE=%date: =_%
set DATE=%DATE:/=%
set LOGPATH=%ROOT%\\log
set SLOTID=1

:: run scripts
%REBOTPATH% --name FinalReport --outputdir %LOGPATH% %LOGPATH%\\%DATE%_SLOT%SLOTID%\\*.xml
pause
