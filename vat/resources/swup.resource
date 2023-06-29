*** Settings ***
Resource    generic.resource
Library    ../library/GenericHelper.py
Library    ../api/PuttyHelper.py
Library    ../api/AgentHelper.py
Library    OperatingSystem

*** Keywords ***
Enter Recovery Mode
    [Documentation]    enter recovery mode
    GenericHelper.Prompt Command    adb root
    generic.Route EngineeringMode
    GenericHelper.Prompt Command    adb shell am broadcast -a android.intent.action.MEDIA_MOUNTED -d file:/test/usb1 -f 0x01000000
    # click upgrade button
    GenericHelper.Prompt Command    adb shell input tap 960 170
    # click enter recovery mode
    GenericHelper.Prompt Command    adb shell input tap 2400 240
Check Image
    [Documentation]    check image exist
    [Arguments]    ${image}
    ${udisk}    GenericHelper.Get Removable Drives
    Directory Should Exist    ${udisk}//${image}    Software package not found!
Check SWUP Success
    ${RES}    AgentHelper.Req To Test Profile    1    Android_Home
    Should Be Equal    ${RES}    ${0}