*** Settings ***
Library    ../api/AgentHelper.py    WITH NAME    magent
Resource    generic.resource
Variables    ../conf/powercycle.py

*** Keywords ***
CheckPowerCycle
    [Documentation]    Execute powercycle and check trace

    generic.PowerCyclebyCMD

CheckDisplay
    [Documentation]    Check profile display using webcam
    
    ${RES}    magent.Req To Test Profile    index=${1}    prof_name=Android_Home
    Should Be Equal    ${RES}    ${0}    Profile does not match!