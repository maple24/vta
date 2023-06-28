*** Settings ***
Library    ../library/GenericHelper.py
Library    OperatingSystem

*** Keywords ***
Enter Recovery Mode
    [Documentation]    enter recovery mode

Triger Upgrade
    [Documentation]    triger upgrade

Check Image
    [Documentation]    check image exist
    [Arguments]    ${image}
    ${udisk}    GenericHelper.Get Removable Drives
    Directory Should Exist    ${udisk}//${image}    Software package not found!
Check Log