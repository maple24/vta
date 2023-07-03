*** Settings ***
Library    ../vat/library/SystemHelper.py
Library    ../vat/library/GenericHelper.py
Library    OperatingSystem
Variables    ../vat/conf/template_settings.py

*** Test Cases ***
Example
    Log To Console    ${ROOT}
    ${tmp}    Join Path    ${ROOT}    tmp
    Log To Console    ${tmp}
    SystemHelper.Android Screencapture    1234567    test1    ${tmp}
    SystemHelper.Android Screencapture    1234567    test2    ${tmp}
    GenericHelper.Image Diff    ${tmp}//test1    ${tmp}//test2