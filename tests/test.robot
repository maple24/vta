# simple-test.robot
*** Settings ***
Library             Collections
Library             String
Library             GeventLibrary
Library             ../vta/api/TSmasterAPI/TSClient.py

*** Keywords ***
Sleep Wrapper
    Sleep    1s

*** Test Cases ***
Test1
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

Test2
    [Documentation]    ...
    &{dTSMaster}    Create Dictionary    tsmaster_enabled=${True}    tsmaster_rbs=123    tsmaster_channel_vgm=${0}    tsmaster_channel_vddm=${1}        
    TSClient.Init Tsmaster    ${dTSMaster}
    TSClient.Start Simulation
    TSClient.Set Signal    0/BackboneFR/CEM/CemBackBoneFr02/VehModMngtGlbSafe1UsgModSts    11
    TSClient.Set Signal    0/BackboneFR/CEM/CemBackBoneFr02/VehModMngtGlbSafe1_UB    1
    TSClient.Get Signal    0/BackboneFR/CEM/CemBackBoneFr02/VehModMngtGlbSafe1UsgModSts
    TSClient.Get Signal    0/BackboneFR/CEM/CemBackBoneFr02/VehModMngtGlbSafe1_UB
    TSClient.Stop Simulation

Test3
    ${test}    Set Variable    ${None}
    Should Not Be Equal As Strings    ${test}    ${None}