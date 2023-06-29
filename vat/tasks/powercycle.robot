*** Settings ***
Resource    ../resources/powercycle.resource
Resource    ../resources/generic.resource
Resource    ../resources/qvta.resource
Library    ../api/AgentHelper.py
# Library    ../api/TSmasterAPI/TSClient.py

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
    
    Run Keyword If    '${STEPS}[${TEST_NAME}][type]'=='command'    powercycle.Reset by CMD
    IF    '${STEPS}[${TEST_NAME}][type]'=='network'
        # ${RES}    ${MATCHED}    PuttyHelper.Wait For Trace    pattern=(LCM Shutdown)    cmd=bosch_reset    timeout=30    login=${False}
        # Should Be Equal    ${RES}    ${True}    Fail to get shutdown trace!
        AgentHelper.Req To Set Voltage    1    1    0
        Sleep    0.5s
        AgentHelper.Req To Set Voltage    1    1    12
        # RelayHelper.Set Relay Port    dev_type=xinke    port_index=1    state_code=1
        # Sleep    0.5s
        # RelayHelper.Set Relay Port    dev_type=xinke    port_index=1    state_code=0
        # Sleep    0.5s

        # TSClient.Init Tsmaster    ${${SLOT}}[dtsmaster]
        # TSClient.Startup
        ${RES}    ${MATCHED}    PuttyHelper.Wait For Trace    pattern=(Startup done)    timeout=60    login=${False}
        Should Be Equal    ${RES}    ${True}    Fail to get startup trace!
    END
    Sleep    10s

StepCheckOMS
    [Tags]
    qvta.Open OMS
    ${RES}    AgentHelper.Req To Test Profile    ${1}    OMS
    Should Be Equal    ${RES}    ${0}
    qvta.Exit Camera

StepCheckDMS
    [Tags]
    qvta.Open DMS
    ${RES}    AgentHelper.Req To Test Profile    ${1}    DMS
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
    ${STEPS}[${TEST_NAME}][displays]
