*** Settings ***
Library    ../library/putty_helper.py    WITH NAME    mPutty
Variables    ../conf/base.py

*** Test Cases ***
TC1
    [Documentation]    ...

    Log To Console    helloworld
    mPutty.Connect    ${dputty}