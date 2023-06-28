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
    ${image}    qvta.Download_Latest
    generic.UDisk2PC
    ${udisk}    GenericHelper.Get Removable Drives
    FileManager.Copy Directory    ${image}    ${udisk}//all_images
    generic.UDisk2DHU

Media_Picture
    [Documentation]    open picture in USB3.0
    # open picture

    # check display

BSP_Camera_DMS
    [Documentation]    check DMS camera
    qvta.Open_DMS
    ${RES}    AgentHelper.Req To Test Profile    1    DMS
    generic.Putty_CtrlC
    Should Be Equal    ${RES}    ${0}    Profile does not match!

BSP_Camera_OMS
    [Documentation]    check OMS camera
    qvta.Open_OMS
    ${RES}    AgentHelper.Req To Test Profile    1    OMS
    generic.Putty_CtrlC
    Should Be Equal    ${RES}    ${0}    Profile does not match!

BSP_Display_CSD
    [Documentation]    check CSD display
    generic.Route_Carlauncher
    ${RES}    AgentHelper.Req To Test Profile    1    Android_Home
    Should Be Equal    ${RES}    ${0}    Profile does not match!

BSP_Display_Backlight
    [Documentation]    check backlight in CSD
    qvta.Open_Backlight
    ${RES}    AgentHelper.Req To Test Profile    1    Backlight
    generic.Putty_CtrlC
    Should Be Equal    ${RES}    ${0}    Profile does not match!

LCM_PowerONOFF
    [Documentation]    power on/off switch via ACC
    generic.ACC_OFF
    ${RES1}    AgentHelper.Req To Test Profile    1    Black_Screen
    Should Be Equal    ${RES1}    ${0}    Profile does not match!
    generic.ACC_ON
    ${RES2}    AgentHelper.Req To Test Profile    1    Android_Home
    Should Be Equal    ${RES2}    ${0}    Profile does not match!