*** Settings ***
Library    ../api/PuttyHelper.py
Library    ../api/RelayHelper.py
Library    ../library/GenericHelper.py
Library    ../api/AgentHelper.py
Library    ../api/DLTHelper.py
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
    [Arguments]    ${adbid}
    GenericHelper.Prompt Command    adb -s ${adbid} shell am start -n com.android.car.carlauncher/.CarLauncher
Route Files
    [Arguments]    ${adbid}
    GenericHelper.Prompt Command    adb -s ${adbid} shell am start -n com.android.documentsui/.LauncherActivity
Route EngineeringMode
    [Arguments]    ${adbid}
    GenericHelper.Prompt Command    adb -s ${adbid} shell am start -n com.bosch.apps.engineeringmode/.MainActivity
Route BT Settings
    [Arguments]    ${adbid}
    GenericHelper.Prompt Command    adb -s ${adbid} shell am start -a android.settings.BLUETOOTH_SETTINGS
Route WIFI Settings
    [Arguments]    ${adbid}
    GenericHelper.Prompt Command    adb -s ${adbid} shell am start -a android.settings.WIFI_SETTINGS
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
    [Arguments]    ${cameraindex}=${1}
    AgentHelper.Req To Stop Video    ${cameraindex}
    AgentHelper.Req To Start Video    ${cameraindex}
WebCam Video OFF
    [Arguments]    ${cameraindex}=${1}
    AgentHelper.Req To Stop Video    ${cameraindex}
Check Android Home
    [Arguments]    ${cameraindex}=${1}
    ${RES}    AgentHelper.Req To Test Profile    ${cameraindex}    Android_Home
    Should Be Equal    ${RES}    ${0}    Android Home does not match!
Check Black Screen
    [Arguments]    ${cameraindex}=${1}
    ${RES}    AgentHelper.Req To Test Profile    ${cameraindex}    Black_Screen
    Should Be Equal    ${RES}    ${0}    Black Screen does not match!
Check Upgrade Screen
    [Arguments]    ${cameraindex}=${1}
    ${RES}    AgentHelper.Req To Test Profile    ${cameraindex}    Upgrade
    Should Be Equal    ${RES}    ${0}    Upgrade Screen does not match!
Check USB Picture
    [Arguments]    ${cameraindex}=${1}
    ${RES}    AgentHelper.Req To Test Profile    ${cameraindex}    USB
    Should Be Equal    ${RES}    ${0}    USB picture does not match!
Check Android Home and Thermal
    [Arguments]    ${cameraindex}
    PuttyHelper.Send Command And Return Traces    cat /dev/thermalmgr
    Check Android Home    ${cameraindex}
Check Trace From Container
    [Arguments]    ${pattern}
    @{traces}=    PuttyHelper.Get Trace Container
    ${RES}    ${matched}=    GenericHelper.Match String    ${pattern}    ${traces}
    Should Be Equal    ${RES}    ${True}    Fail to match pattern ${pattern}!
INIT
    [Documentation]    Init all instances
    [Arguments]    ${CONF}
    PuttyHelper.Connect    dPutty=${CONF}[dputty]
    PuttyHelper.Enable Monitor
    RelayHelper.Init Relay    drelay=${CONF}[drelay]
    DLTHelper.Connect    dDlt=${CONF}[ddlt]
    DLTHelper.Enable Monitor
    Define Global
DEINIT
    [Documentation]    Deinit all instances
    PuttyHelper.Disconnect
    PuttyHelper.Disable Monitor
    DLTHelper.Disconnect
    DLTHelper.Disable Monitor
Define Global
    [Documentation]    Define global variables
    ${TESTER}    GenericHelper.Get Username
    ${BENCHID}    GenericHelper.Get Ip
    Set Global Variable    ${TESTER}
    Set Global Variable    ${BENCHID}