*** Settings ***
Resource    ../resources/powercycle.resource
Variables    ../conf/bench_setup.py

# Test Setup    setups.INIT    ${${SLOT}}
# Test Teardown    setups.DEINIT

*** Variables ***
# default slot
${SLOT}    SLOT_2
${subject}    Hello world!
${body}    This is mail body!

*** Test Cases ***
TC1
    [Tags]    example
    generic.HelloWorld

# TC2
#     @{list}    Create List    dumping to hello.core    dumping to world.core
#     @{ex_filters}    Create List    hello.core
#     ${RES}    ${matched}=    GenericHelper.Match String    dumping to (.*)    ${list}
#     IF    ${RES} == ${False}    Log To Console    OK
#     FOR    ${element}    IN    @{matched}
#         Log To Console    ${element}[0]
#         List Should Contain Value    ${ex_filters}    ${element}[0]    Detect crash ${element}[0]!
#     END
