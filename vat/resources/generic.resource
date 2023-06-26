*** Settings ***
Library    ../api/PuttyHelper.py
Library    ../api/RelayHelper.py
Library    ../library/GenericHelper.py

*** Keywords ***
HelloWorld
    [Documentation]    helloworld
    Log To Console    helloworld
    
INIT
    [Documentation]    Init all instances
    [Arguments]    ${CONF}
    PuttyHelper.Connect    dPutty=${CONF}[dputty]
    PuttyHelper.Enable Monitor
    RelayHelper.Init Relay    drelay=${CONF}[drelay]

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

GetSOCVersion
    [Documentation]    Get SOC version with putty command 'cat buildinfo.txt'
    
    ${RES}    ${MATCHED}    PuttyHelper.Wait For Trace    pattern=MAIN_VERSION\=(.*)    cmd=cat /mnt/Buildinfo.txt    timeout=10
    Should Be Equal    ${RES}    ${True}    Unable to get SOC version
    
    RETURN    ${MATCHED}

GetSCCVersion
    [Documentation]    Get SCC version with putty command 'swup_scc -i 1'

    ${RES}    ${MATCHED}    PuttyHelper.Wait For Trace    pattern=SCC FW Version Info: (.*)    cmd=swup_scc -i 1    timeout=10
    Should Be Equal    ${RES}    ${True}    Unable to get SCC version
    
    RETURN    ${MATCHED}