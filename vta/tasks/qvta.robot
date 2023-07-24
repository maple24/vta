*** Settings ***
Resource    ../resources/generic.resource
Resource    ../resources/qvta.resource
Resource    ../resources/swup.resource

Library    ../api/AgentHelper.py
Library    ../api/RelayHelper.py
Library    ../library/FileManager.py
Library    ../library/GenericHelper.py
Library    OperatingSystem

Variables    ../conf/settings.py

Suite Setup    generic.INIT    ${CONF_BASE}
Suite Teardown    generic.DEINIT

*** Variables ***
${SLOT}    SLOT_1
${CONF_BASE}    ${${SLOT}}
${SWUP_timeout}    30 minutes
${mail_subject}    Zeekr QVTa
${image_name}    all_images


*** Test Cases ***
SWUP
    [Documentation]    software upgrade
    ${image_path}    qvta.Download Latest
    generic.UDisk to PC
    ${udisk}    GenericHelper.Get Removable Drives
    FileManager.Copy Directory    ${image_path}    ${udisk}//${image_name}
    generic.UDisk to DHU
    swup.Enter Recovery Mode
    swup.Check SWUP Success    ${SWUP_timeout}
    
Media Picture
    [Documentation]    open picture in USB3.0
    # open picture
    qvta.Mount USB to Android
    generic.Route Files
    qvta.Open Picture in USB
    generic.Check USB Picture

BSP Camera DMS
    [Documentation]    check DMS camera
    qvta.Open DMS
    ${RES}    AgentHelper.Req To Test Profile    ${1}    DMS
    qvta.Exit Camera
    Should Be Equal    ${RES}    ${0}    DMS profile does not match!

BSP Camera OMS
    [Documentation]    check OMS camera
    qvta.Open OMS
    ${RES}    AgentHelper.Req To Test Profile    ${1}    OMS
    qvta.Exit Camera
    Should Be Equal    ${RES}    ${0}    OMS profile does not match!

BSP Display CSD
    [Documentation]    check CSD display
    generic.Route Carlauncher
    generic.Check Android Home

BSP Display Backlight
    [Documentation]    check backlight in CSD
    qvta.Open Backlight
    ${RES}    AgentHelper.Req To Test Profile    ${1}    Backlight
    qvta.Exit Camera
    Should Be Equal    ${RES}    ${0}    Backloght does not match!

LCM PowerONOFF
    [Documentation]    power on/off switch via ACC
    generic.ACC OFF
    generic.Check Black Screen
    generic.ACC ON
    generic.Check Android Home