*** Settings ***
Resource    ../resources/base.resource

*** Test Cases ***
TC1
    [Documentation]    ...

    Log To Console    helloworld
    mPutty.Connect    ${dputty}