*** Settings ***
Resource    ../resources/powercycle.resource

Test Setup    setups.INIT
Test Teardown    setups.DEINIT

*** Test Cases ***
TC1
    [Documentation]    ...
    [Tags]    example
    generic.HelloWorld
    powercycle.CheckPowerCycle