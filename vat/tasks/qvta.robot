*** Settings ***
Resource    ../resources/generic.resource
Resource    ../resources/qvta.resource
Resource    ../resources/swup.resource

Library    ../api/AgentHelper.py
Library    ../api/RelayHelper.py
Library    ../api/TSmasterAPI/TSClient.py
Library    ../library/FileManager.py
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
    ${udisk}    FileManager.Get Removable Drives
    FileManager.Copy Directory    ${image}    ${udisk}//all_images
    generic.UDisk2DHU

Media_Picture
    [Documentation]    open picture in USB3.0
    # open picture

    # check display

BSP_Camera_DMS
    [Documentation]    check DMS camera
    # turn on camera
    qvta.Open_DMS
    # check camera display
    AgentHelper.Req To Test Profile    1    DMS
    generic.Putty_CtrlC

BSP_Camera_OMS
    [Documentation]    check OMS camera
    qvta.Open_OMS
    AgentHelper.Req To Test Profile    1    OMS
    generic.Putty_CtrlC

BSP_Display_CSD
    [Documentation]    check CSD display
    generic.Route_Carlauncher
    AgentHelper.Req To Test Profile    1    Android_Home

BSP_Display_Backlight
    [Documentation]    check backlight in CSD
    qvta.Open_Backlight
    AgentHelper.Req To Test Profile    1    Backlight
    generic.Putty_CtrlC

LCM_PowerONOFF
    [Documentation]    power on/off switch via ACC
    generic.ACC_OFF
    AgentHelper.Req To Test Profile    1    Black_Screen
    generic.ACC_ON
    AgentHelper.Req To Test Profile    1    Android_Home