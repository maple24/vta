*** Settings ***
Library    ../conf/powercycle_setup.py
Resource    ../resources/powercycle.resource

*** Test Cases ***
TC
    [Documentation]    ...
    Run Keyword If    condition    CheckDisplay    $index    $profile