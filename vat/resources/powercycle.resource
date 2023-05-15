*** Settings ***
Library    ../api/AgentHelper.py    WITH NAME    magent
Resource    generic.resource

*** Keywords ***
Test
    [Documentation]    ...
    [Arguments]    ${args}    ${enabled}=${True}
    Log To Console    ${args}
    

CheckPowerCycle
    [Documentation]    Execute powercycle and check trace
    [Arguments]    ${type}
    Run Keyword If    ${type}==command    generic.PowerCyclebyCMD
    Run Keyword If    ${type}==network    generic.PowerCyclebyCAN

CheckDisplay
    [Documentation]    Check profile display using webcam
    [Arguments]    ${index}    ${profile}
    ${RES}    magent.Req To Test Profile    index=${index}    prof_name=${profile}
    Should Be Equal    ${RES}    ${0}    Profile does not match!

CheckCrash
    [Documentation]    Check if crash happens
    [Arguments]    ${dInputParameters}
    
    @{aPuttyTraces}=    mPutty.Get Trace Container
    ${bFoundSub}    ${aDetectedTraces}=    mgeneric.Match String    ${aPuttyTraces}    dumping to

    [Return]    ${RESULT}