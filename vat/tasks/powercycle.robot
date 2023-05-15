*** Settings ***
Resource    ../resources/powercycle.resource
Resource    ../resources/setups.resource
Library    Collections
Variables    ../conf/bench_setup.py
Variables    ../conf/powercycle_setup.py

Suite Setup    setups.INIT    ${${SLOT}}
Suite Teardown    setups.DEINIT    ${MESSAGE_CONTAINER}

Test Teardown    Append To List    ${MESSAGE_CONTAINER}    ${TEST_MESSAGE}

*** Variables ***
${SLOT}    SLOT_1
${SLOT_POWERCYCLE}    ${${SLOT}_POWERCYCLE}
${STEPS}    ${${SLOT}_POWERCYCLE}[steps]
@{MESSAGE_CONTAINER}

*** Test Cases ***
StepTest
    [Tags]
    [Template]    powercycle.Test
    ${STEPS}[${TEST_NAME}][name]

StepCheckPowerCycle
    [Tags]    skip
    [Template]    powercycle.CheckPowerCycle
    ${STEPS}[${TEST_NAME}][type]
    
StepCheckDisplays
    [Tags]    skip
    [Template]    powercycle.CheckDisplay
    ${STEPS}[${TEST_NAME}][displays]

StepCheckCrash
    [Tags]    skip
    [Template]    powercycle.CheckCrash
    ${STEPS}[${TEST_NAME}][type]