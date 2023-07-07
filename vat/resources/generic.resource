*** Settings ***
Library    ../api/PuttyHelper.py
Library    ../api/RelayHelper.py
Library    ../library/GenericHelper.py
Library    ../library/FileManager.py
Library    ../api/AgentHelper.py
Library    OperatingSystem

*** Keywords ***
Hello World
    [Documentation]    helloworld
    Log To Console    helloworld
    # Should Be Equal    1    2
Randomly Run Keywords
    [Documentation]    run keywords randomly
    [Arguments]    ${keyword_list}
    ${random_keyword}    Evaluate    random.choice($keyword_list)
    Run Keyword    ${random_keyword}
Auto Log Pull
    [Documentation]    pull log to usb disk automatically
    UDisk to PC
    ${udisk}    GenericHelper.Get Removable Drives
    Create File    ${udisk}//zeekr-auto-export.txt
    UDisk to DHU
Route Carlauncher
    GenericHelper.Prompt Command    adb shell am start -n com.android.car.carlauncher/.CarLauncher
Route Files
    GenericHelper.Prompt Command    adb shell am start -n com.android.documentsui/.LauncherActivity
Route EngineeringMode
    GenericHelper.Prompt Command    adb shell am start -n com.bosch.apps.engineeringmode/.MainActivity
Route BT Settings
    GenericHelper.Prompt Command    adb shell am start -a android.settings.BLUETOOTH_SETTINGS
Route WIFI Settings
    GenericHelper.Prompt Command    adb shell am start -a android.settings.WIFI_SETTINGS
Putty CtrlC
    PuttyHelper.Send Command And Return Traces    \x03    login=${False}
ACC ON
    RelayHelper.Set Relay Port    dev_type=xinke    port_index=2    state_code=0
ACC OFF
    RelayHelper.Set Relay Port    dev_type=xinke    port_index=2    state_code=1
Power ON with Relay
    RelayHelper.Set Relay Port    dev_type=xinke    port_index=1    state_code=0
Power OFF with Relay
    RelayHelper.Set Relay Port    dev_type=xinke    port_index=1    state_code=1
Power ON with PPS
    AgentHelper.Req To Set Voltage    1    1    12
Power OFF with PPS
    AgentHelper.Req To Set Voltage    1    1    0
UDisk to PC
    RelayHelper.Set Relay Port    dev_type=cleware    port_index=1    state_code=1
    Sleep    1s
UDisk to DHU
    RelayHelper.Set Relay Port    dev_type=cleware    port_index=5    state_code=1
    Sleep    1s
WebCam Video ON
    AgentHelper.Req To Stop Video    1
    AgentHelper.Req To Start Video    1
WebCam Video OFF
    AgentHelper.Req To Stop Video    1
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
    Set Global Variable    ${TESTER}
    Set Global Variable    ${BENCHID}