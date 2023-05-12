*** Settings ***
Library    ../api/AgentHelper.py    WITH NAME    magent
Resource    generic.resource

*** Keywords ***
CheckPowerCycle
    [Documentation]    Execute powercycle and check trace

    generic.PowerCyclebyCMD

CheckDisplay
    [Documentation]    Check profile display using webcam
    [Arguments]    ${index}    ${profile}

    ${RES}    magent.Req To Test Profile    index=${index}    prof_name=${profile}
    Should Be Equal    ${RES}    ${0}    Profile does not match!