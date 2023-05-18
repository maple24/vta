*** Settings ***
Resource    ../resources/powercycle.resource
Resource    ../resources/setups.resource
Variables    ../conf/bench_setup.py

# Test Setup    setups.INIT    ${${SLOT}}
# Test Teardown    setups.DEINIT

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
    @{list}    Create List    dumping to hello.core    dumping to world.core
    @{ex_filters}    Create List    hello.core
    ${RES}    ${matched}=    GenericHelper.Match String    dumping to (.*)    ${list}
    IF    ${RES} == ${False}    Log To Console    OK
    FOR    ${element}    IN    @{matched}
        Log To Console    ${element}[0]
        List Should Contain Value    ${ex_filters}    ${element}[0]    Detect crash ${element}[0]!
    END
    