*** Settings ***
Library    ../api/AgentHelper.py
Library    Collections
Resource    generic.resource
Library    ../library/PuttyHelper.py
Library    ../library/GenericHelper.py

*** Keywords ***
Test
    [Documentation]    ...
    [Arguments]    ${name}

    Log To Console    ${name}
    Should Be Equal    123    1    force failure

INIT
    [Documentation]    Init all instances
    [Arguments]    ${CONF}
    PuttyHelper.Connect    dPutty=${CONF}[dputty]
    PuttyHelper.Enable Monitor

    DefineGlobal

DEINIT
    [Documentation]    Deinit all instances
    PuttyHelper.Disconnect
    PuttyHelper.Disable Monitor

DefineGlobal
    [Documentation]    Define global variables
    ${TESTER}    GenericHelper.Get Username
    ${BENCHID}    GenericHelper.Get Hostname
    # ${SOCVersion}    generic.GetSOCVersion
    # ${SCCVersion}    generic.GetSCCVersion
    Set Global Variable    ${TESTER}
    Set Global Variable    ${BENCHID}
    # Set Global Variable    ${SOCVersion}
    # Set Global Variable    ${SCCVersion}

CheckDisplay
    [Documentation]    Check profile display using webcam, args: list
    [Arguments]    ${dispalys}

    FOR    ${element}    IN    @{dispalys}
        ${RES}    Run Keyword If    ${element}[index]!=${0}    AgentHelper.Req To Test Profile    ${element}[index]   ${element}[profile]
        Run Keyword If    ${RES}!=${None}    Should Be Equal    ${RES}    ${0}    Profile does not match!
    END

CheckCrash
    [Documentation]    Check if crash happens
    [Arguments]    ${ex_filters}
    
    @{traces}=    PuttyHelper.Get Trace Container
    ${RES}    ${matched}=    GenericHelper.Match String    dumping to (.*)    ${traces}
    IF    ${RES} == ${False}    RETURN
    FOR    ${element}    IN    @{matched}
        List Should Contain Value    ${ex_filters}    ${element}[0]    Detect crash ${element}[0]!
    END

CheckNormalTrace
    [Documentation]    Check trace from putty trace container
    [Arguments]    ${patterns}
    
    @{traces}    PuttyHelper.Get Trace Container
    FOR    ${element}    IN    @{patterns}
        ${RES}    ${matched}=    GenericHelper.Match String    ${element}    ${traces}
        Should Be Equal    ${RES}    ${True}    Trace not found! ${element}
    END

CheckErrorTrace
    [Documentation]    Inspect if ramdump trace pattern appeared in putty trace container
    [Arguments]    ${patterns}

    @{traces}    PuttyHelper.Get Trace Container
    FOR    ${element}    IN    @{patterns}
        ${RES}    ${matched}=    GenericHelper.Match String    ${element}    ${traces}
        Should Not Be Equal    ${RES}    ${True}    Error trace detected! ${element}
    END