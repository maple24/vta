*** Settings ***
Resource    ../resources/base.resource

*** Test Cases ***
TC1
    [Documentation]    ...

    base.HelloWorld
    mPutty.Connect    ${dputty}