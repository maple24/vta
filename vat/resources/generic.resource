*** Settings ***
Library    ../library/PuttyHelper.py
Library    ../library/GenericHelper.py

*** Keywords ***
HelloWorld
    [Documentation]    helloworld
    Log To Console    helloworld
    
GetSOCVersion
    [Documentation]    Get SOC version with putty command 'cat buildinfo.txt'
    
    ${RES}    ${MATCHED}    PuttyHelper.Wait For Trace    attern=MAIN_VERSION\=(.*)    cmd=cat Buildinfo.txt    timeout=5
    Should Be Equal    ${RES}    ${True}    Unable to get SOC version
    
    RETURN    ${MATCHED}

GetSCCVersion
    [Documentation]    Get SCC version with putty command 'swup_scc -i 1'

    ${RES}    ${MATCHED}    PuttyHelper.Wait For Trace    pattern=SCC FW Version Info: (.*)    cmd=swup_scc -i 1    timeout=5
    Should Be Equal    ${RES}    ${True}    Unable to get SCC version
    RETURN    ${MATCHED}

ResetbyCMD
    [Documentation]    Run powercycle with putty command 'bosch_reset'

    ${RES}    ${MATCHED}    PuttyHelper.Wait For Trace    pattern=(LCM Unmount is done successfully)    cmd=bosch_reset    timeout=50
    Should Be Equal    ${RES}    ${True}    Fail to get shutdown trace!

ResetbyCAN
    [Documentation]    Run powercycle with can signals