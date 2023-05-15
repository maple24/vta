*** Settings ***
Resource    ../resources/powercycle.resource
Variables    ../conf/bench_setup.py
Variables    ../conf/powercycle_setup.py

*** Variables ***
${SLOT}    SLOT_1
${SLOT_POWERCYCLE}    ${${SLOT}_POWERCYCLE}
${STEPS}    ${${SLOT}_POWERCYCLE}[steps]

*** Test Cases ***
StepTest
    [Tags]    123
    powercycle.Test    ${STEPS}[${TEST_NAME}][args]
    # Should Be Equal    1    2

StepPowerCycle
    [Tags]    234
    Log To Console    ${SLOT_1}
    Log To Console    ${STEPS}
# StepCheckDisplay
#     [Tags]    skip
#     [Template]    CheckDisplay
#     ${1}    Android_Home
#     ${1}    Cluster_Home

StepCheckCrash
    [Tags]    123
    Log To Console    123