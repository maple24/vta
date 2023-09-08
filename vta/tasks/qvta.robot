*** Settings ***
Resource    ../resources/generic.resource
Resource    ../resources/qvta.resource
Resource    ../resources/swup.resource

Library    ../api/AgentHelper.py
Library    ../api/RelayHelper.py
Library    ../library/GenericHelper.py
Library    OperatingSystem

Variables    ../conf/settings.py

Suite Setup    generic.INIT    ${CONF_BASE}
Suite Teardown    generic.DEINIT

*** Variables ***
${SLOT}    SLOT_1
${CONF_BASE}    ${${SLOT}}
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
    qvta.Mount USB to QNX    ${CAMERA_INDEX}
    swup.Enter Recovery Mode
    swup.Check SWUP Success    ${SWUP_timeout}    ${CAMERA_INDEX}

BT
    [Documentation]    click bluetooth button
    [Tags]    skip

WIFI
    [Documentation]    click wifi button
    [Tags]    skip

Media Picture
    [Documentation]    open picture in USB3.0
    # open picture
    qvta.Mount USB to Android    ${CAMERA_INDEX}
    generic.Route Files
    qvta.Open Picture in USB
    generic.Check USB Picture    ${CAMERA_INDEX}
    # qvta.Mount USB to QNX

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
    generic.Route Carlauncher
    generic.Check Android Home    ${CAMERA_INDEX}

BSP Display Backlight
    [Documentation]    check backlight in CSD
    qvta.Open Backlight
    ${RES}    AgentHelper.Req To Test Profile    ${CAMERA_INDEX}    Backlight
    generic.Putty CtrlC
    Should Be Equal    ${RES}    ${0}    Backloght does not match!

LCM PowerONOFF
    [Documentation]    power on/off switch via ACC
    generic.Power OFF with Relay
    Sleep    0.5s
    generic.Check Black Screen    ${CAMERA_INDEX}
    generic.Power ON with Relay
    Wait Until Keyword Succeeds    2 minutes    5s    generic.Check Android Home    ${CAMERA_INDEX}