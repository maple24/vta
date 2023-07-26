*** Settings ***
Resource    ../../resources/generic.resource
Library    ../../library/GenericHelper.py
Library    ../../library/SystemHelper.py

Variables    ../../conf/settings.py
Variables    coordinates.py

Suite Setup    Get Device ID

*** Keywords ***
Get Device ID
    ${device_id_list}    SystemHelper.Get Adb Devices
    ${device_number}    Get Length    ${device_id_list}
    Should Be Equal As Integers    ${device_number}    ${1}
    Set Suite Variable    ${device_id}    ${device_id_list}[0]
Click ZEEKR BT Button
    GenericHelper.Prompt Command    adb shell input tap ${BT_BUTTON_ZEEKR}[0] ${BT_BUTTON_ZEEKR}[1]    
    Sleep    2s
Click ZEEKR WIFI Button
    GenericHelper.Prompt Command    adb shell input tap ${WIFI_BUTTON_ZEEKR}[0] ${WIFI_BUTTON_ZEEKR}[1]    
Click BT Button
    GenericHelper.Prompt Command    adb shell input tap ${BT_BUTTON}[0] ${BT_BUTTON}[1]
Click WIFI Button
    GenericHelper.Prompt Command    adb shell input tap ${WIFI_BUTTON}[0] ${WIFI_BUTTON}[1]
Route Zeekr BT Settings
    Route Zeekr Car Launcher
    Route Zeekr Car Settings
    GenericHelper.Prompt Command    adb shell input tap ${BT_SETTINGS_ZEEKR}[0] ${BT_SETTINGS_ZEEKR}[1]  
Route ZEEKR WIFI Settings
    Log To Console    unready
Route Zeekr Car Settings
    GenericHelper.Prompt Command    adb shell input tap ${CAR_SETTINGS_ZEEKR}[0] ${CAR_SETTINGS_ZEEKR}[1]
Route Zeekr Car Launcher
    GenericHelper.Prompt Command    adb shell input tap ${CAR_LAUNCHER_ZEEKR}[0] ${CAR_LAUNCHER_ZEEKR}[1]

*** Test Cases ***
BT
    [Documentation]    click bt on/off button and check status change
    [Tags]
    [Setup]    generic.Route BT Settings
    GenericHelper.Prompt Command    adb shell input tap ${BT_SETTINGS}[0] ${BT_SETTINGS}[1]
    ${BT_0}    SystemHelper.Android Screencapture    ${device_id}    BT_0.png    ${TEMP}
    Click BT Button
    ${BT_1}    SystemHelper.Android Screencapture    ${device_id}    BT_1.png    ${TEMP}
    ${RES}    GenericHelper.Image Diff    ${BT_0}    ${BT_1}
    Should Not Be Equal    ${RES}    ${True}
    
WIFI
    [Documentation]    click wifi on/off button and check status change
    [Tags]    
    [Setup]    generic.Route WIFI Settings
    ${WIFI_0}    SystemHelper.Android Screencapture    ${device_id}    WIFI_0.png    ${TEMP}
    Click WIFI Button
    ${WIFI_1}    SystemHelper.Android Screencapture    ${device_id}    WIFI_1.png    ${TEMP}
    ${RES}    GenericHelper.Image Diff    ${WIFI_0}    ${WIFI_1}    thre=${0.1}
    Should Not Be Equal    ${RES}    ${True}
ZEEKR BT
    [Documentation]    click bt on/off button and check status change
    [Tags]    skip
    [Setup]    Route ZEEKR BT Settings
    ${BT_0}    SystemHelper.Android Screencapture    ${device_id}    BT_0.png    ${TEMP}
    Click ZEEKR BT Button
    ${BT_1}    SystemHelper.Android Screencapture    ${device_id}    BT_1.png    ${TEMP}
    ${RES}    GenericHelper.Image Diff    ${BT_0}    ${BT_1}    thre=${0.5}
    Should Not Be Equal    ${RES}    ${True}
    
ZEEKR WIFI
    [Documentation]    click wifi on/off button and check status change
    [Tags]    skip
    [Setup]    Route ZEEKR WIFI Settings
    ${WIFI_0}    SystemHelper.Android Screencapture    ${device_id}    WIFI_0.png    ${TEMP}
    Click ZEEKR WIFI Button
    ${WIFI_1}    SystemHelper.Android Screencapture    ${device_id}    WIFI_1.png    ${TEMP}
    ${RES}    GenericHelper.Image Diff    ${WIFI_0}    ${WIFI_1}    thre=${0.1}
    Should Not Be Equal    ${RES}    ${True}