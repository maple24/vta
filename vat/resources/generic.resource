*** Settings ***
Library    ../api/PuttyHelper.py
Library    ../api/RelayHelper.py
Library    ../library/GenericHelper.py
Library    ../library/FileManager.py
Library    ../../.venv/lib/site-packages/robot/libraries/OperatingSystem.py

*** Keywords ***
Hello World
    [Documentation]    helloworld
    Log To Console    helloworld
    Should Be Equal    1    2
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
POWER ON
    RelayHelper.Set Relay Port    dev_type=xinke    port_index=1    state_code=0
POWER OFF
    RelayHelper.Set Relay Port    dev_type=xinke    port_index=1    state_code=1
Route Carlauncher
    GenericHelper.Prompt Command    adb shell am start -n com.android.car.carlauncher/.CarLauncher
Route Files
    GenericHelper.Prompt Command    adb shell am start -n com.android.documentsui/.LauncherActivity
Route EngineeringMode
    GenericHelper.Prompt Command    adb shell am start -n com.bosch.apps.engineeringmode/.MainActivity
UDisk to PC
    RelayHelper.Set Relay Port    dev_type=cleware    port_index=1    state_code=1
UDisk to DHU
    RelayHelper.Set Relay Port    dev_type=cleware    port_index=5    state_code=1
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