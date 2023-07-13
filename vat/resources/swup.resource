*** Settings ***
Resource    generic.resource
Library    ../library/GenericHelper.py
Library    ../api/PuttyHelper.py
Library    ../api/AgentHelper.py
Library    OperatingSystem

*** Keywords ***
Enter Recovery Mode
    [Documentation]    enter recovery mode
    generic.Route EngineeringMode
    # click upgrade button
    GenericHelper.Prompt Command    adb shell input tap 600 160
    Sleep    1s
    # click enter recovery mode
    GenericHelper.Prompt Command    adb shell input tap 2400 240
    Sleep    1s
    @{traces}=    PuttyHelper.Get Trace Container
    ${RES}    ${matched}=    GenericHelper.Match String    (Requester: usbdownload)    ${traces}
    Should Be Equal    ${RES}    ${True}    Fail to enter recovery mode!
    Wait Until Keyword Succeeds    3 minutes    10 sec    generic.Check Upgrade Screen
Check Image
    [Documentation]    check image exist
    [Arguments]    ${image}
    ${udisk}    GenericHelper.Get Removable Drives
    Directory Should Exist    ${udisk}//${image}    Software package not found!
Check SWUP Success
    [Arguments]    ${SWUP_timeout}
    Wait Until Keyword Succeeds    ${SWUP_timeout}    10 sec    generic.Check Android Home