*** Settings ***
Resource    ../resources/generic.resource
Resource    ../resources/qvta.resource
Resource    ../resources/swup.resource
Resource    ../resources/powercycle.resource

Library    ../api/AgentHelper.py
Library    ../api/RelayHelper.py
Library    ../api/DLTHelper.py
Library    ../library/GenericHelper.py
Library    ../library/SystemHelper.py
Library    ../api/ArtifaHelper.py    ${repo}    ${pattern}    ${server}    ${dunder}
Library    OperatingSystem

Variables    ../conf/settings.py

Suite Setup    generic.INIT    ${CONF_BASE}
Suite Teardown    generic.DEINIT


*** Variables ***
${SLOT}    SLOT_1
${CONF_BASE}    ${${SLOT}}
${ADB_ID}    ${CONF_BASE}[adbid]
${CAMERA_INDEX}    ${CONF_BASE}[cameraindex]
${SWUP_timeout}    30 minutes
${mail_subject}    Zeekr QVTa
${image_name}    all_images
${server}    https://rb-cmbinex-szh-p1.apac.bosch.com/artifactory/
${repo}    zeekr-dhu-repos/builds/rb-zeekr-dhu_hqx424-pcs01_main_dev/daily/
${pattern}    _userdebug.tgz$
@{dunder}    ets1szh    estbangbangde6


*** Keywords ***
Download From Artifactory
    [Documentation]    download latest version from artifactory and unzip
    [Arguments]    ${url}=${None}
    IF    $url == $None
        ${source}    ArtifaHelper.Get Latest
        Should Not Be Equal As Strings    ${source}    ${None}    Fail to get latest version!
        ${url}    Set Variable    ${source}[url]
    END
    ${package}    ArtifaHelper.Download    ${url}
    File Should Exist    ${package}    File not exist!
    ArtifaHelper.Unzip    ${package}
    ${image}    ArtifaHelper.Get Swpath    name=all_images_8295
    Directory Should Exist    ${image}    Image directory does not exist!
    RETURN    ${image}


*** Test Cases ***
SWUP
    [Documentation]    software upgrade
    ${image_path}    Download From Artifactory
    generic.UDisk to PC
    ${udisk}    GenericHelper.Get Removable Drives
    Remove Directory    ${udisk}//${image_name}    recursive=${True}
    Move Directory    ${image_path}    ${udisk}//${image_name}
    generic.UDisk to DHU
    swup.Enter Recovery Mode    ${ADB_ID}
    swup.Check SWUP Success    ${SWUP_timeout}    ${CAMERA_INDEX}    ${ADB_ID}

GetVersion
    [Documentation]    get soc version
    ${SOCVersion}    qvta.Get SOC Version
    Set Suite Variable    ${SOCVersion}

System Partition
    [Documentation]    system_b  3G
    [Tags]    
    @{traces}    PuttyHelper.Send Command And Return Traces    cmd=df -g /dev/disk/system_b    wait=${1.0}
    ${RES}    ${matched}=    GenericHelper.Match String    (\\d+)\\s+total.*\\[(\\d+).*\\]    ${traces}
    Should Be Equal    ${RES}    ${True}    Fail to match pattern `(\\d+)\\s+total.*\\[(\\d+).*\\]`
    ${result}    Evaluate    (float($matched[0][0]) * float($matched[0][1])) / 1024 / 1024 / 1024
    Should Be Equal    ${result}    ${3.0}

BT
    [Documentation]    click bluetooth button
    [Tags]    
    [Setup]    generic.Route BT Settings    ${ADB_ID}
    GenericHelper.Prompt Command    adb -s ${ADB_ID} shell input tap 250 215
    ${BT_0}    SystemHelper.Android Screencapture    ${ADB_ID}    BT_0.png    ${TEMP}
    GenericHelper.Prompt Command    adb -s ${ADB_ID} shell input tap 2400 220
    ${BT_1}    SystemHelper.Android Screencapture    ${ADB_ID}    BT_1.png    ${TEMP}
    ${RES}    GenericHelper.Image Diff    ${BT_0}    ${BT_1}
    Should Not Be Equal    ${RES}    ${True}

WIFI
    [Documentation]    click wifi button
    [Tags]    
    [Setup]    generic.Route WIFI Settings    ${ADB_ID}
    ${WIFI_0}    SystemHelper.Android Screencapture    ${ADB_ID}    WIFI_0.png    ${TEMP}
    GenericHelper.Prompt Command    adb -s ${ADB_ID} shell input tap 2400 220
    ${WIFI_1}    SystemHelper.Android Screencapture    ${ADB_ID}    WIFI_1.png    ${TEMP}
    ${RES}    GenericHelper.Image Diff    ${WIFI_0}    ${WIFI_1}    thre=${0.1}
    Should Not Be Equal    ${RES}    ${True}

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

BSP Display Cluster
    [Documentation]    check CSD display
    [Tags]    skip

BSP Display Backlight
    [Documentation]    check backlight in CSD
    qvta.Open Backlight
    ${RES}    AgentHelper.Req To Test Profile    ${CAMERA_INDEX}    Backlight
    generic.Putty CtrlC
    Should Be Equal    ${RES}    ${0}    Backlight does not match!

LCM PowerONOFF
    [Documentation]    power on/off switch via ACC
    [Tags]    
    generic.Power OFF with Relay
    Sleep    0.5s
    generic.Check Black Screen    ${CAMERA_INDEX}
    generic.Power ON with Relay
    Wait Until Keyword Succeeds    2 minutes    5s    generic.Check Android Home    ${CAMERA_INDEX}

DLT Log
    [Documentation]    startup log in dlt
    # PowerM: POWERM_SM_RUN_STATE
    DLTHelper.Connect    dDlt=${CONF_BASE}[ddlt]
    DLTHelper.Enable Monitor
    powercycle.Reset by PPS    ${CAMERA_INDEX}
    qvta.Check DLT
    DLTHelper.Disable Monitor
    DLTHelper.Disconnect

Android Reboot
    [Documentation]    reboot by android command: adb -s 1234567 reboot
    powercycle.Reset by Android Command    ${CAMERA_INDEX}    ${ADB_ID}

Media Picture
    [Documentation]    open picture in USB3.0
    # open picture
    generic.Route Files    ${ADB_ID}
    qvta.Open Picture in USB    ${ADB_ID}
    Sleep    1s
    generic.Check USB Picture    ${CAMERA_INDEX}
    generic.Route Carlauncher    ${ADB_ID}

Audio 1kHz
    [Documentation]    test audio with 1000khz
    generic.Route Files    ${ADB_ID}
    qvta.Open Audio in USB    ${ADB_ID}
    Wait Until Keyword Succeeds    30s    1s    generic.Check 1Hz Audio
    generic.Route Carlauncher    ${ADB_ID}