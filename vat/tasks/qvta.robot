*** Settings ***
Resource    ../resources/generic.resource
Resource    ../resources/qvta.resource
Resource    ../resources/swup.resource

Library    ../api/AgentHelper.py
Library    ../api/RelayHelper.py
Library    ../library/FileManager.py
Library    ../library/GenericHelper.py
Library    OperatingSystem

Variables    ../conf/bench_setup.py

Suite Setup    generic.INIT    ${CONF_BASE}
Suite Teardown    generic.DEINIT

*** Variables ***
${SLOT}    SLOT_1
${CONF_BASE}    ${${SLOT}}


*** Test Cases ***
SWUP
    [Documentation]    software upgrade
    ${image}    qvta.Download Latest
    generic.UDisk to PC
    ${udisk}    GenericHelper.Get Removable Drives
    FileManager.Copy Directory    ${image}    ${udisk}//all_images
    generic.UDisk to DHU
    swup.Enter Recovery Mode
    swup.Triger Upgrade

Media Picture
    [Documentation]    open picture in USB3.0
    # open picture

    # check display

BSP Camera DMS
    [Documentation]    check DMS camera
    qvta.Open DMS
    ${RES}    AgentHelper.Req To Test Profile    1    DMS
    generic.Putty CtrlC
    Should Be Equal    ${RES}    ${0}    Profile does not match!

BSP Camera OMS
    [Documentation]    check OMS camera
    qvta.Open OMS
    ${RES}    AgentHelper.Req To Test Profile    1    OMS
    generic.Putty CtrlC
    Should Be Equal    ${RES}    ${0}    Profile does not match!

BSP Display CSD
    [Documentation]    check CSD display
    generic.Route Carlauncher
    ${RES}    AgentHelper.Req To Test Profile    1    Android_Home
    Should Be Equal    ${RES}    ${0}    Profile does not match!

BSP Display Backlight
    [Documentation]    check backlight in CSD
    qvta.Open Backlight
    ${RES}    AgentHelper.Req To Test Profile    1    Backlight
    generic.Putty CtrlC
    Should Be Equal    ${RES}    ${0}    Profile does not match!

LCM PowerONOFF
    [Documentation]    power on/off switch via ACC
    generic.ACC OFF
    ${RES1}    AgentHelper.Req To Test Profile    1    Black_Screen
    Should Be Equal    ${RES1}    ${0}    Profile does not match!
    generic.ACC ON
    ${RES2}    AgentHelper.Req To Test Profile    1    Android_Home
    Should Be Equal    ${RES2}    ${0}    Profile does not match!