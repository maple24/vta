*** Settings ***
Resource    ../resources/generic.resource
Resource    ../resources/qvta.resource
Library    ../api/AgentHelper.py
Library    ../api/RelayHelper.py
Library    ../api/TSmasterAPI/TSClient.py

Variables    ../conf/bench_setup.py

Suite Setup    generic.INIT    ${CONF_BASE}
Suite Teardown    generic.DEINIT

*** Variables ***
${SLOT}    SLOT_1
${CONF_BASE}    ${${SLOT}}

*** Test Cases ***
SWUP
    [Documentation]    software upgrade
    # enter discovery mode

    # triger upgrade

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
    qvta.Putty_CtrlC

BSP_Camera_OMS
    [Documentation]    check OMS camera
    qvta.Open_OMS
    AgentHelper.Req To Test Profile    1    OMS
    qvta.Putty_CtrlC

BSP_Display_CSD
    [Documentation]    check CSD display
    qvta.Route_Carlauncher
    AgentHelper.Req To Test Profile    1    Android_Home

BSP_Display_Backlight
    [Documentation]    check backlight in CSD
    qvta.Open_Backlight
    AgentHelper.Req To Test Profile    1    Backlight
    qvta.Putty_CtrlC

LCM_PowerONOFF
    [Documentation]    power on/off switch via ACC
    ACC_OFF
    AgentHelper.Req To Test Profile    1    Black_Screen
    ACC_ON
    AgentHelper.Req To Test Profile    1    Android_Home