*** Settings ***
Resource    ../resources/powercycle.resource
Resource    ../resources/setups.resource

Variables    ../conf/bench_setup.py
Variables    ../conf/powercycle_setup.py

Suite Setup    setups.INIT    ${CONF_BASE}
Suite Teardown    setups.DEINIT

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
    [Template]    powercycle.CheckPowerCycle
    ${STEPS}[${TEST_NAME}][type]
    
StepCheckDisplays
    [Tags]
    [Template]    powercycle.CheckDisplay
    ${STEPS}[${TEST_NAME}][displays]

StepCheckCrash
    [Tags]
    [Template]    powercycle.CheckCrash
    ${STEPS}[${TEST_NAME}][type]