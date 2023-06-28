*** Settings ***
Library    ../api/PuttyHelper.py
Library    ../api/RelayHelper.py
Library    ../library/GenericHelper.py

*** Keywords ***
Hello World
    [Documentation]    helloworld
    Log To Console    helloworld
Randomly Run Keywords
    [Documentation]    run keywords randomly
    [Arguments]    ${keyword_list}
    ${random_keyword}    Evaluate    random.choice($keyword_list)
    Run Keyword    ${random_keyword}
Putty CtrlC
    PuttyHelper.Send Command    \x03
ACC ON
    RelayHelper.Set Relay Port    dev_type=xinke    port_index=2    state_code=0
ACC OFF
    RelayHelper.Set Relay Port    dev_type=xinke    port_index=2    state_code=1
Route Carlauncher
    GenericHelper.Prompt Command    adb shell am start com.android.car.carlauncher/.CarLauncher
UDisk to PC
    RelayHelper.Set Relay Port    dev_type=multiplexer    port_index=14
UDisk to DHU
    RelayHelper.Set Relay Port    dev_type=multiplexer    port_index=24
INIT
    [Documentation]    Init all instances
    [Arguments]    ${CONF}
    PuttyHelper.Connect    dPutty=${CONF}[dputty]
    PuttyHelper.Enable Monitor
    RelayHelper.Init Relay    drelay=${CONF}[drelay]
    Define Global
DEINIT
    [Documentation]    Deinit all instances
    PuttyHelper.Disconnect
    PuttyHelper.Disable Monitor
Define Global
    [Documentation]    Define global variables
    ${TESTER}    GenericHelper.Get Username
    ${BENCHID}    GenericHelper.Get Hostname
    # ${SOCVersion}    qvta.Get SOC Version
    # ${SCCVersion}    qvta.Get SCC Version
    Set Global Variable    ${TESTER}
    Set Global Variable    ${BENCHID}
    # Set Global Variable    ${SOCVersion}
    # Set Global Variable    ${SCCVersion}