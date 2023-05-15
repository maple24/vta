*** Settings ***
Library    ../api/AgentHelper.py
Resource    generic.resource

*** Keywords ***
Test
    [Documentation]    ...
    [Arguments]    ${name}
    Log To Console    ${name}
    Should Be Equal    123    1    force failure

CheckPowerCycle
    [Documentation]    Execute powercycle and check trace, agrs: str
    [Arguments]    ${type}
    Run Keyword If    '${type}'=='command'    generic.ResetbyCMD
    Run Keyword If    '${type}'=='network'    generic.ResetbyCAN

CheckDisplay
    [Documentation]    Check profile display using webcam, args: list
    [Arguments]    ${dispalys}
    FOR    ${element}    IN    @{dispalys}
        ${RES}    Run Keyword And Return If    ${element}[index]!=${0}    AgentHelper.Req To Test Profile    ${element}[index]   ${element}[profile]
        Should Be Equal    ${RES}    ${0}    Profile does not match!
    END

CheckCrash
    [Documentation]    Check if crash happens
    [Arguments]    ${dInputParameters}
    
    @{traces}=    mPutty.Get Trace Container
    ${RES}    ${matched}=    mgeneric.Match String    ${traces}    (dumping to)


CheckStartupTrace
    [Documentation]    Check trace from putty trace container
    @{traces}    mputty.Get Trace Container

    ${RES}    ${matched}=    mgeneric.Match String    ${traces}    (Log Type: B)
    Should Be Equal    ${RES}    ${True}    Startup trace not found!

CheckRamdump
    [Documentation]    Inspect if ramdump trace pattern appeared in putty trace container

    @{traces}=    mPutty.Get Trace Container
    ${RES}    ${matched}=    mgeneric.Match String    ${traces}    (XBLRamDump Image Loaded)
    Should Not Be Equal    ${RES}    ${True}    Ramdump occurs!