*** Settings ***
Library             Collections
Library             String
Library             GeventLibrary

*** Test Cases ***
ASYNC
    [Documentation]    Simple test flow with gevent greenlets
    Log    Hello World
    ${msg}    Set Variable    1
    Create Gevent Bundle    alias=alias1  # Create a bundle of coroutines
    # register all your keywords as coroutines to the gevent bundle
    Add Coroutine    Sleep    1s    alias=alias1
    Add Coroutine    Log To Console    message=${msg}    alias=alias1
    Add Coroutine    Log To Console    message=2    alias=alias1
    Add Coroutine    Convert To Lower Case    UPPER    alias=alias1
    # Run your coroutines and get the values by order
    @{values}    Run Coroutines    alias=alias1
    Log Many    @{values}
    Log To Console    ${values}[3]