*** Settings ***
Resource    ../../resources/powercycle.resource
Resource    ../../resources/generic.resource
Resource    ../../resources/qvta.resource
Library    ../../api/AgentHelper.py
Library    ../../api/TSmasterAPI/TSCOM.py

Variables    ../../conf/settings.py
Variables    ../../conf/setups.py

Suite Setup    generic.INIT    ${CONF_BASE}
Suite Teardown    generic.DEINIT

*** Variables ***
${SLOT}    SLOT_1
${CONF_BASE}    ${${SLOT}}
${CONF_TEST}    ${${SLOT}_POWERCYCLE}
${STEPS}    ${CONF_TEST}[steps]
${ADB_ID}    ${CONF_BASE}[adbid]
${CAMERA_INDEX}    ${CONF_BASE}[cameraindex]
${mail_subject}    Powercycle error notification!
${mail_body}    Unexpected error occurs!!


*** Test Cases ***
StepTest
    [Tags]
    [Template]    powercycle.Test
    ${STEPS}[${TEST_NAME}][name]
    ${STEPS}[${TEST_NAME}][name]

GetVersion
    ${SOCVersion}    qvta.Get SOC Version
    Set Suite Variable    ${SOCVersion}
StepCheckPowerCycle
    [Tags]
    [Setup]    Run Keyword If    ${VIDEO}==${True}    generic.WebCam Video ON    ${CAMERA_INDEX}
    [Teardown]    Run Keyword If    ${VIDEO}==${True}    generic.WebCam Video OFF    ${CAMERA_INDEX}
    IF    '${STEPS}[${TEST_NAME}][type]'=='command'
        Log    run powercycle with putty command
        ${RES}    ${MATCHED}    PuttyHelper.Wait For Trace    pattern=(LCM Shutdown)    cmd=bosch_reset -b normal    timeout=30
        Should Be True    ${RES}    Fail to get shutdown trace!
    ELSE IF    '${STEPS}[${TEST_NAME}][type]'=='pps'
        Log    run powercycle with pps
        generic.Power OFF with PPS
        Sleep    1s
        generic.Power ON with PPS
        Sleep    5s
        generic.Power OFF with PPS
        Sleep    1s
        generic.Power ON with PPS
    ELSE IF    '${STEPS}[${TEST_NAME}][type]'=='relay'
        Log    run powercycle with pps
        generic.Power OFF with Relay
        Sleep    1s
        generic.Power ON with Relay
    ELSE IF    '${STEPS}[${TEST_NAME}][type]'=='network'
        Log    run powercycle with network
        TSCOM.Shutdown
        Sleep    0.5s
        TSCOM.Startup
    ELSE IF    '${STEPS}[${TEST_NAME}][type]'=='acc'
        Log    run powercycle with acc
        generic.ACC OFF
        Sleep    1s
        generic.ACC ON
    END
    ${RES}    ${MATCHED}    PuttyHelper.Wait For Trace    pattern=(Startup done)    timeout=60    login=${False}
    Should Be True    ${RES}    Fail to get startup trace!
    Wait Until Keyword Succeeds    2 minutes    5 sec    generic.Check Android Home and Thermal    ${CAMERA_INDEX}

StepCheckOMS
    [Tags]
    qvta.Open OMS
    ${RES}    AgentHelper.Req To Test Profile    ${CAMERA_INDEX}    OMS
    Should Be Equal    ${RES}    ${0}
    qvta.Exit Camera

StepCheckDMS
    [Tags]
    qvta.Open DMS
    ${RES}    AgentHelper.Req To Test Profile    ${CAMERA_INDEX}    DMS
    Should Be Equal    ${RES}    ${0}
    qvta.Exit Camera

StepCheckCrash
    [Tags]
    [Template]    powercycle.Check Crash
    ${STEPS}[${TEST_NAME}][ex_filters]
    
StepCheckNormalTrace
    [Tags]
    [Template]    powercycle.Check Normal Trace
    ${STEPS}[${TEST_NAME}][patterns]

StepCheckErrorTrace
    [Tags]
    [Template]    powercycle.Check Error Trace
    ${STEPS}[${TEST_NAME}][patterns]

StepCheckDisplays
    [Tags]
    [Template]    powercycle.Check Display
    ${STEPS}[${TEST_NAME}][displays]    ${CAMERA_INDEX}
