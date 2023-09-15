*** Settings ***
Resource    ../../resources/powercycle.resource
Resource    ../../resources/generic.resource
Resource    ../../resources/qvta.resource
Library    ../../api/TSmasterAPI/TSClient.py
Library    ../../api/APIFlexClient.py

Variables    ../../conf/settings.py

Suite Setup    generic.INIT    ${CONF_BASE}
Suite Teardown    generic.DEINIT


*** Variables ***
${SLOT}    SLOT_1
${CONF_BASE}    ${${SLOT}}
${senario}    command
@{crash_filters}        audio_service.core
@{normal_traces}    (Log Type: B)
@{error_traces}    (XBLRamDump Image Loaded)


*** Keywords ***
Check Android Home and Thermal
    PuttyHelper.Send Command And Return Traces    cat /dev/thermalmgr
    IF    ${VIDEO} == ${True}
        ${RES}    APIFlexClient.Req To Test Profile    Android_Home
        Should Be Equal    ${RES}    ${True}
    END


*** Test Cases ***
GetVersion
    [Documentation]    get socversion
    [Tags]
    ${SOCVersion}    qvta.Get SOC Version
    Set Suite Variable    ${SOCVersion}
CheckPowerCycle
    [Tags]
    [Setup]    Run Keyword If    ${VIDEO}==${True}    APIFlexClient.Req To Start Video
    [Teardown]    Run Keyword If    ${VIDEO}==${True}    APIFlexClient.Req To Stop Video
    IF    '${senario}'=='command'
        Log    run powercycle with putty command
        ${RES}    ${MATCHED}    PuttyHelper.Wait For Trace    pattern=(LCM Shutdown)    cmd=bosch_reset -b normal    timeout=30
        Should Be Equal    ${RES}    ${True}    Fail to get shutdown trace!
    ELSE IF    '${senario}'=='pps'
        Log    run powercycle with pps
        generic.Power OFF with PPS
        Sleep    0.5s
        generic.Power ON with PPS
        Sleep    5s
        generic.Power OFF with PPS
        Sleep    0.5s
        generic.Power ON with PPS
    ELSE IF    '${senario}'=='relay'
        Log    run powercycle with pps
        generic.Power OFF with Relay
        Sleep    0.5s
        generic.Power ON with Relay
    ELSE IF    '${senario}'=='network'
        Log    run powercycle with network
        TSClient.Init Tsmaster    ${${SLOT}}[dtsmaster]
        TSClient.Shutdown
        Sleep    0.5s
        TSClient.Startup
    ELSE IF    '${senario}'=='acc'
        Log    run powercycle with acc
        generic.ACC OFF
        Sleep    0.5s
        generic.ACC ON
    END
    ${RES}    ${MATCHED}    PuttyHelper.Wait For Trace    pattern=(Pull up)    timeout=60    login=${False}
    Should Be Equal    ${RES}    ${True}    Fail to get startup trace!
    Wait Until Keyword Succeeds    2 minutes    5 sec    Check Android Home and Thermal
CheckCrash
    [Tags]
    [Template]    powercycle.Check Crash
    ${crash_filters}
CheckNormalTrace
    [Documentation]    traces should appear in traces
    [Tags]    skip
    [Template]    powercycle.Check Normal Trace
    ${normal_traces}
CheckErrorTrace
    [Documentation]    traces should not appear in traces
    [Tags]    skip
    [Template]    powercycle.Check Error Trace
    ${error_traces}