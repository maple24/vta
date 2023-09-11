*** Settings ***
Resource    ../resources/generic.resource
Resource    ../resources/qvta.resource
Resource    ../resources/swup.resource

Library    ../api/AgentHelper.py
Library    ../api/RelayHelper.py
Library    ../api/DLTHelper.py
Library    ../library/GenericHelper.py
Library    ../library/SystemHelper.py
Library    OperatingSystem

Variables    ../conf/settings.py

Suite Setup    generic.INIT    ${CONF_BASE}
Suite Teardown    generic.DEINIT

*** Variables ***
${SLOT}    SLOT_1
${CONF_BASE}    ${${SLOT}}
${ADB_ID}    ${CONF_BASE}[cameraindex]
${CAMERA_INDEX}    ${CONF_BASE}[cameraindex]
${SWUP_timeout}    30 minutes
${mail_subject}    Zeekr QVTa
${image_name}    all_images


*** Test Cases ***
SWUP
    [Documentation]    software upgrade
    ${image_path}    qvta.Download Latest
    generic.UDisk to PC
    ${udisk}    GenericHelper.Get Removable Drives
    Remove Directory    ${udisk}//${image_name}    recursive=${True}
    Move Directory    ${image_path}    ${udisk}//${image_name}
    generic.UDisk to DHU
    swup.Enter Recovery Mode    ${ADB_ID}
    swup.Check SWUP Success    ${SWUP_timeout}    ${CAMERA_INDEX}    ${ADB_ID}

BT
    [Documentation]    click bluetooth button
    [Tags]    skip
    [Setup]    generic.Route BT Settings    ${ADB_ID}
    GenericHelper.Prompt Command    adb shell input tap 250 215
    ${BT_0}    SystemHelper.Android Screencapture    ${ADB_ID}    BT_0.png    ${TEMP}
    GenericHelper.Prompt Command    adb shell input tap 2400 220
    ${BT_1}    SystemHelper.Android Screencapture    ${ADB_ID}    BT_1.png    ${TEMP}
    ${RES}    GenericHelper.Image Diff    ${BT_0}    ${BT_1}
    Should Not Be Equal    ${RES}    ${True}

WIFI
    [Documentation]    click wifi button
    [Tags]    skip
    [Setup]    generic.Route WIFI Settings    ${ADB_ID}
    ${WIFI_0}    SystemHelper.Android Screencapture    ${ADB_ID}    WIFI_0.png    ${TEMP}
    GenericHelper.Prompt Command    adb shell input tap 2400 220
    ${WIFI_1}    SystemHelper.Android Screencapture    ${ADB_ID}    WIFI_1.png    ${TEMP}
    ${RES}    GenericHelper.Image Diff    ${WIFI_0}    ${WIFI_1}    thre=${0.1}
    Should Not Be Equal    ${RES}    ${True}

Media Picture
    [Documentation]    open picture in USB3.0
    # open picture
    generic.Route Files    ${ADB_ID}
    qvta.Open Picture in USB    ${ADB_ID}
    generic.Check USB Picture    ${CAMERA_INDEX}

BSP Camera DMS
    [Documentation]    check DMS camera
    qvta.Open DMS
    ${RES}    AgentHelper.Req To Test Profile    ${CAMERA_INDEX}    DMS
    qvta.Exit Camera
    Should Be Equal    ${RES}    ${0}    DMS profile does not match!

BSP Camera OMS
    [Documentation]    check OMS camera
    qvta.Open OMS
    ${RES}    AgentHelper.Req To Test Profile    ${CAMERA_INDEX}    OMS
    qvta.Exit Camera
    Should Be Equal    ${RES}    ${0}    OMS profile does not match!

BSP Display CSD
    [Documentation]    check CSD display
    generic.Route Carlauncher    ${ADB_ID}
    generic.Check Android Home    ${CAMERA_INDEX}

BSP Display Backlight
    [Documentation]    check backlight in CSD
    qvta.Open Backlight
    ${RES}    AgentHelper.Req To Test Profile    ${CAMERA_INDEX}    Backlight
    generic.Putty CtrlC
    Should Be Equal    ${RES}    ${0}    Backlight does not match!

LCM PowerONOFF
    [Documentation]    power on/off switch via ACC
    generic.Power OFF with Relay
    Sleep    0.5s
    generic.Check Black Screen    ${CAMERA_INDEX}
    generic.Power ON with Relay
    Wait Until Keyword Succeeds    2 minutes    5s    generic.Check Android Home    ${CAMERA_INDEX}

DLT Log
    [Documentation]    startup log in dlt
    # PowerM: POWERM_SM_RUN_STATE
    generic.Power OFF with PPS
    Sleep    0.5s
    generic.Check Black Screen    ${CAMERA_INDEX}
    generic.Power ON with PPS
    Wait Until Keyword Succeeds    2 minutes    5s    generic.Check Android Home    ${CAMERA_INDEX}
    @{traces}=    DLTHelper.Get Trace Container
    ${RES}    ${matched}=    GenericHelper.Match String    (POWERM_SM_RUN_STATE)    ${traces}
    Should Be Equal    ${RES}    ${True}    Fail to match pattern `POWERM_SM_RUN_STATE`!