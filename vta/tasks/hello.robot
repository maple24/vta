*** Settings ***
Resource    ../resources/generic.resource
Variables    ../conf/settings.py

# Test Setup    setups.INIT    ${${SLOT}}
# Test Teardown    setups.DEINIT

*** Variables ***
# default slot
${SLOT}    SLOT_2
${mail_subject}    Hello world!
${mail_body}    This is mail body!

*** Test Cases ***
TC1
    [Tags]    skip
    [Setup]    Run Keyword If    ${VIDEO}==${True}    generic.WebCam Video ON
    [Teardown]    Run Keyword If    ${VIDEO}==${True}    generic.WebCam Video OFF
    generic.Hello World
    
# TC2
#     @{list}    Create List    dumping to hello.core    dumping to world.core
#     @{ex_filters}    Create List    hello.core
#     ${RES}    ${matched}=    GenericHelper.Match String    dumping to (.*)    ${list}
#     IF    ${RES} == ${False}    Log To Console    OK
#     FOR    ${element}    IN    @{matched}
#         Log To Console    ${element}[0]
#         List Should Contain Value    ${ex_filters}    ${element}[0]    Detect crash ${element}[0]!
#     END

TC3
    Wait Until Keyword Succeeds    1 minutes    10 sec    generic.Hello World

TC4
    Wait Until Keyword Succeeds    1 minutes    10 sec    generic.Hello World