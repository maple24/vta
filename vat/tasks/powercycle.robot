*** Settings ***
Resource    ../resources/powercycle.resource
Library    ../api/TSmasterAPI/TSClient.py
Variables    ../conf/bench_setup.py
Variables    ../conf/powercycle_setup.py

Suite Setup    powercycle.INIT    ${CONF_BASE}
Suite Teardown    powercycle.DEINIT

*** Variables ***
${SLOT}    SLOT_1
${CONF_BASE}    ${${SLOT}}
${CONF_TEST}    ${${SLOT}_POWERCYCLE}
${STEPS}    ${CONF_TEST}[steps]

*** Test Cases ***
StepTest
    [Tags]
    [Template]    powercycle.Test
    ${STEPS}[${TEST_NAME}][name]

StepCheckPowerCycle
    [Tags]
    
    Run Keyword If    '${STEPS}[${TEST_NAME}][type]'=='command'    generic.ResetbyCMD
    IF    '${STEPS}[${TEST_NAME}][type]'=='network'
        ${RES}    ${MATCHED}    PuttyHelper.Wait For Trace    pattern=(LCM Shutdown)    cmd=bosch_reset    timeout=30    login=${False}
        Should Be Equal    ${RES}    ${True}    Fail to get shutdown trace!
        
        TSClient.Init Tsmaster    ${${SLOT}}[dtsmaster]
        TSClient.Startup
        ${RES}    ${MATCHED}    PuttyHelper.Wait For Trace    pattern=(LCM Startup Condition)    timeout=60    login=${False}
        Should Be Equal    ${RES}    ${True}    Fail to get startup trace!
    END
    Sleep    10s

StepCheckCrash
    [Tags]
    [Template]    powercycle.CheckCrash
    ${STEPS}[${TEST_NAME}][ex_filters]
    
StepCheckNormalTrace
    [Tags]
    [Template]    powercycle.CheckNormalTrace
    ${STEPS}[${TEST_NAME}][patterns]

StepCheckErrorTrace
    [Tags]
    [Template]    powercycle.CheckErrorTrace
    ${STEPS}[${TEST_NAME}][patterns]

StepCheckDisplays
    [Tags]
    [Template]    powercycle.CheckDisplay
    ${STEPS}[${TEST_NAME}][displays]
