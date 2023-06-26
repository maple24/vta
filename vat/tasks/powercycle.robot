*** Settings ***
Resource    ../resources/powercycle.resource
Resource    ../resources/generic.resource
Library    ../api/TSmasterAPI/TSClient.py

Variables    ../conf/bench_setup.py
Variables    ../conf/powercycle_setup.py

Suite Setup    generic.INIT    ${CONF_BASE}
Suite Teardown    generic.DEINIT

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
    ${STEPS}[${TEST_NAME}][name]

StepCheckPowerCycle
    [Tags]
    
    Run Keyword If    '${STEPS}[${TEST_NAME}][type]'=='command'    powercycle.ResetbyCMD
    IF    '${STEPS}[${TEST_NAME}][type]'=='network'
        # ${RES}    ${MATCHED}    PuttyHelper.Wait For Trace    pattern=(LCM Shutdown)    cmd=bosch_reset    timeout=30    login=${False}
        # Should Be Equal    ${RES}    ${True}    Fail to get shutdown trace!
        RelayHelper.Set Relay Port    dev_type=xinke    port_index=1    state_code=1
        Sleep    0.5s
        RelayHelper.Set Relay Port    dev_type=xinke    port_index=1    state_code=0
        Sleep    0.5s

        TSClient.Init Tsmaster    ${${SLOT}}[dtsmaster]
        TSClient.Startup
        # ${RES}    ${MATCHED}    PuttyHelper.Wait For Trace    pattern=(Startup done)    timeout=60    login=${False}
        # Should Be Equal    ${RES}    ${True}    Fail to get startup trace!
    END
    Sleep    55s

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
