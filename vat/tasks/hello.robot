*** Settings ***
Resource    ../resources/powercycle.resource
Resource    ../resources/setups.resource
Variables    ../conf/bench_setup.py

Test Setup    setups.INIT    ${${SLOT}}
Test Teardown    setups.DEINIT

*** Variables ***
# default slot
${SLOT}    SLOT_2

*** Test Cases ***
TC1
    [Tags]    example
    generic.HelloWorld
    # Log To Console    ${${SLOT}}[dputty]
    # Should Be Equal    1    2
    # Log To Console    ${SLOT}[dputty]
    # powercycle.CheckPowerCycle
TC2
    generic.HelloWorld