*** Settings ***
Library    ../api/AgentHelper.py
Library    Collections
Resource    generic.resource
Library    ../library/PuttyHelper.py
Library    ../library/GenericHelper.py
Library    ../api/TSmasterAPI/TSClient.py

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
    TSClient.Init Tsmaster    ${CONF}[dtsmaster]

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

ZEEKR_ResetbyCAN
    [Documentation]    ...

    ZEEKR_ShutdownbyCAN
    ${RES}    ${MATCHED}    PuttyHelper.Wait For Trace    pattern=(LCM killed)    cmd=bosch_reset    timeout=30
    Should Be Equal    ${RES}    ${True}    Fail to get shutdown trace!

    ZEEKR_StartupbyCAN
    Sleep    0.5s
    ZEEKR_StartupbyCAN
    ${RES}    ${MATCHED}    PuttyHelper.Wait For Trace    pattern=(Log Type: B)    timeout=60
    Should Be Equal    ${RES}    ${True}    Fail to get startup trace!

ZEEKR_StartupbyCAN
    [Documentation]    ...

    TSClient.Start Simulation
    TSClient.Set Signal    0/BackboneFR/CEM/CemBackBoneFr02/VehModMngtGlbSafe1UsgModSts    11
    TSClient.Set Signal    0/BackboneFR/CEM/CemBackBoneFr02/VehModMngtGlbSafe1_UB    1
    TSClient.Get Signal    0/BackboneFR/CEM/CemBackBoneFr02/VehModMngtGlbSafe1UsgModSts
    TSClient.Get Signal    0/BackboneFR/CEM/CemBackBoneFr02/VehModMngtGlbSafe1_UB
    TSClient.Stop Simulation

ZEEKR_ShutdownbyCAN
    [Documentation]    ...

    TSClient.Start Simulation
    TSClient.Set Signal    0/BackboneFR/CEM/CemBackBoneFr02/VehModMngtGlbSafe1UsgModSts    0
    TSClient.Set Signal    0/BackboneFR/CEM/CemBackBoneFr02/VehModMngtGlbSafe1_UB    0
    TSClient.Get Signal    0/BackboneFR/CEM/CemBackBoneFr02/VehModMngtGlbSafe1UsgModSts
    TSClient.Get Signal    0/BackboneFR/CEM/CemBackBoneFr02/VehModMngtGlbSafe1_UB
    TSClient.Stop Simulation


CheckPowerCycle
    [Documentation]    Execute powercycle and check trace, agrs: str
    [Arguments]    ${type}

    Run Keyword If    '${type}'=='command'    generic.ResetbyCMD
    Run Keyword If    '${type}'=='network'    ZEEKR_ResetbyCAN

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