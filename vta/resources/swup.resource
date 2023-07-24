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
    generic.Check Trace From Container    (Requester: usbdownload)
    Wait Until Keyword Succeeds    3 minutes    10 sec    generic.Check Upgrade Screen
Check Image
    [Documentation]    check image exist
    [Arguments]    ${image}
    ${udisk}    GenericHelper.Get Removable Drives
    Directory Should Exist    ${udisk}//${image}    Software package not found!
Check SWUP Success
    [Arguments]    ${SWUP_timeout}
    Wait Until Keyword Succeeds    ${SWUP_timeout}    30 sec    generic.Check Trace From Container    (SwitchToNormal)
    Wait Until Keyword Succeeds    1 minutes    5 sec    generic.Check Android Home
    # close notification
    GenericHelper.Prompt Command    adb shell input tap 865 865