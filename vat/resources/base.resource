*** Settings ***
Library    ../library/PuttyHelper.py    WITH NAME    mputty
Library    ../library/GenericHelper.py    WITH NAME    mgeneric
Variables    ../conf/base.py


*** Keywords ***
HelloWorld
    [Documentation]    helloworld
    Log To Console    helloworld