*** Settings ***
Resource    ../../resources/generic.resource
Resource    ../../resources/swup.resource
Resource    ../../resources/powercycle.resource
Library    ../../api/AgentHelper.py
Library    ../../api/PuttyHelper.py
Library    ../../library/GenericHelper.py

Variables    ../../conf/settings.py

Suite Setup    generic.INIT    ${CONF_BASE}
Suite Teardown    generic.DEINIT

*** Variables ***
${SLOT}    SLOT_1
${CONF_BASE}    ${${SLOT}}
${ADB_ID}    ${CONF_BASE}[adbid]
${CAMERA_INDEX}    ${CONF_BASE}[cameraindex]
${SWUP_timeout}    30 minutes

*** Keywords ***
PowerReset
    generic.Power OFF with Relay
    Sleep    1s
    generic.Power ON with Relay
    ${RES}    ${MATCHED}    PuttyHelper.Wait For Trace    pattern=(Startup done)    timeout=60    login=${False}
    Should Be True    ${RES}    Fail to get startup trace!
    Wait Until Keyword Succeeds    2 minutes    5 sec    generic.Check Android Home and Thermal    ${CAMERA_INDEX}

*** Test Cases ***
StepSwup
    [Tags]
    swup.Enter Recovery Mode    ${ADB_ID}
    swup.Check SWUP Success    ${SWUP_timeout}    ${CAMERA_INDEX}    ${ADB_ID}
StepCheckPowerCycle
    [Tags]    
    [Setup]    Run Keyword If    ${VIDEO}==${True}    generic.WebCam Video ON    ${CAMERA_INDEX}
    [Teardown]    Run Keyword If    ${VIDEO}==${True}    generic.WebCam Video OFF    ${CAMERA_INDEX}
    GenericHelper.Prompt Command    cmd=adb shell sync
    powercycle.Reset by Android Command    ${CAMERA_INDEX}    ${ADB_ID}
    PuttyHelper.Send Command And Return Traces    cmd=sync    wait=${1}
    FOR    ${counter}    IN RANGE    5
        Log    Reset count:${counter}
        PowerReset
    END