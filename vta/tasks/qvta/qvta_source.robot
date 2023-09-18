*** Settings ***
Resource    ../../resources/generic.resource
Resource    ../../resources/qvta.resource
Resource    ../../resources/swup.resource
Resource    ../../resources/powercycle.resource

Library    ../../api/AgentHelper.py
Library    ../../api/RelayHelper.py
Library    ../../api/DLTHelper.py
Library    ../../library/GenericHelper.py
Library    ../../library/SystemHelper.py
Library    ../../api/ArtifaHelper.py    ${repo}    ${pattern}    ${server}    ${dunder}
Library    OperatingSystem

Variables    ../../conf/settings.py

Suite Setup    generic.INIT    ${CONF_BASE}
Suite Teardown    generic.DEINIT


*** Variables ***
${SLOT}    SLOT_1
${CONF_BASE}    ${${SLOT}}
${ADB_ID}    ${CONF_BASE}[adbid]
${CAMERA_INDEX}    ${CONF_BASE}[cameraindex]
${SWUP_timeout}    30 minutes
${image_name}    all_images
${server}    https://rb-cmbinex-szh-p1.apac.bosch.com/artifactory/
${repo}    zeekr-dhu-repos/builds/rb-zeekr-dhu_hqx424-pcs01_main_dev/daily/
${pattern}    _userdebug.tgz$
@{dunder}    ets1szh    estbangbangde6
${mail_subject}    [QVTa Report] ${repo}


*** Keywords ***
Download From Artifactory
    [Documentation]    download latest version from artifactory and unzip
    [Arguments]    ${url}=${None}
    IF    $url == $None
        ${source}    ArtifaHelper.Get Latest Pro
        Should Not Be Equal As Strings    ${source}    ${None}    Fail to get latest version!
        ${url}    Set Variable    ${source}[url]
    END
    ${package}    ArtifaHelper.Download    ${url}
    File Should Exist    ${package}    File not exist!
    ${checksum}    ArtifaHelper.Checksum    ${package}    ${source}[sha1]
    Should Be True    ${checksum}    Checksum does not match!
    ArtifaHelper.Unzip    ${package}
    ${image}    ArtifaHelper.Get Swpath    name=all_images_8295
    Directory Should Exist    ${image}    Image directory does not exist!
    RETURN    ${image}


*** Test Cases ***
SWUP
    [Documentation]    Software upgrade
    ${image_path}    Download From Artifactory
    generic.UDisk to PC
    ${udisk}    GenericHelper.Get Removable Drives
    Remove Directory    ${udisk}//${image_name}    recursive=${True}
    Move Directory    ${image_path}    ${udisk}//${image_name}
    generic.UDisk to DHU
    swup.Enter Recovery Mode    ${ADB_ID}
    swup.Check SWUP Success    ${SWUP_timeout}    ${CAMERA_INDEX}    ${ADB_ID}

Get Version
    [Documentation]    Get soc version from QNX
    ${SOCVersion}    qvta.Get SOC Version
    Set Suite Variable    ${SOCVersion}

System Partition
    [Documentation]    Check system_b partition is 3G
    [Tags]    
    @{traces}    PuttyHelper.Send Command And Return Traces    cmd=df -g /dev/disk/system_b    wait=${1.0}
    ${RES}    ${matched}=    GenericHelper.Match String    (\\d+)\\s+total.*\\[(\\d+).*\\]    ${traces}
    Should Be True    ${RES}    Fail to match pattern `(\\d+)\\s+total.*\\[(\\d+).*\\]`
    ${result}    Evaluate    (float($matched[0][0]) * float($matched[0][1])) / 1024 / 1024 / 1024
    Should Be Equal    ${result}    ${3.0}

BSP Camera DMS
    [Documentation]    Check DMS camera
    qvta.Open DMS
    ${RES}    AgentHelper.Req To Test Profile    ${CAMERA_INDEX}    DMS
    qvta.Exit Camera
    Should Be Equal    ${RES}    ${0}    DMS profile does not match!

BSP Camera OMS
    [Documentation]    Check OMS camera
    qvta.Open OMS
    ${RES}    AgentHelper.Req To Test Profile    ${CAMERA_INDEX}    OMS
    qvta.Exit Camera
    Should Be Equal    ${RES}    ${0}    OMS profile does not match!

BSP Display CSD
    [Documentation]    Check CSD display
    generic.Route Carlauncher    ${ADB_ID}
    Sleep    1s
    generic.Check Android Home    ${CAMERA_INDEX}

BSP Display Cluster
    [Documentation]    Check Cluster display
    [Tags]    skip

BSP Display Backlight
    [Documentation]    Check backlight in CSD
    qvta.Open Backlight
    ${RES}    AgentHelper.Req To Test Profile    ${CAMERA_INDEX}    Backlight
    generic.Putty CtrlC
    Should Be Equal    ${RES}    ${0}    Backlight does not match!

LCM PowerONOFF
    [Documentation]    System wakeup and sleep
    [Tags]    
    generic.Power OFF with Relay
    Sleep    0.5s
    generic.Check Black Screen    ${CAMERA_INDEX}
    generic.Power ON with Relay
    Wait Until Keyword Succeeds    2 minutes    5s    generic.Check Android Home    ${CAMERA_INDEX}

DLT Log
    [Documentation]    Check startup log from dlt
    # PowerM: POWERM_SM_RUN_STATE
    DLTHelper.Connect    dDlt=${CONF_BASE}[ddlt]
    DLTHelper.Enable Monitor
    powercycle.Reset by PPS    ${CAMERA_INDEX}
    qvta.Check DLT
    DLTHelper.Disable Monitor
    DLTHelper.Disconnect

Android Reboot
    [Documentation]    Reboot by android command
    powercycle.Reset by Android Command    ${CAMERA_INDEX}    ${ADB_ID}

BT
    [Documentation]    Click bluetooth button and check status
    [Tags]    
    [Setup]    generic.Route BT Settings    ${ADB_ID}
    GenericHelper.Prompt Command    adb -s ${ADB_ID} shell input tap 250 215
    Sleep    1s
    ${BT_0}    SystemHelper.Android Screencapture    ${ADB_ID}    BT_0.png    ${TEMP}
    GenericHelper.Prompt Command    adb -s ${ADB_ID} shell input tap 2400 220
    Sleep    1s
    ${BT_1}    SystemHelper.Android Screencapture    ${ADB_ID}    BT_1.png    ${TEMP}
    ${RES}    GenericHelper.Image Diff    ${BT_0}    ${BT_1}
    Should Not Be Equal    ${RES}    ${True}

WIFI
    [Documentation]    Click wifi button and check status
    [Tags]    
    [Setup]    generic.Route WIFI Settings    ${ADB_ID}
    ${WIFI_0}    SystemHelper.Android Screencapture    ${ADB_ID}    WIFI_0.png    ${TEMP}
    GenericHelper.Prompt Command    adb -s ${ADB_ID} shell input tap 2400 220
    Sleep    1s
    ${WIFI_1}    SystemHelper.Android Screencapture    ${ADB_ID}    WIFI_1.png    ${TEMP}
    ${RES}    GenericHelper.Image Diff    ${WIFI_0}    ${WIFI_1}    thre=${0.1}
    Should Not Be Equal    ${RES}    ${True}

Media Picture
    [Documentation]    Open picture in USB3.0
    # open picture
    generic.Route Files    ${ADB_ID}
    qvta.Open Picture in USB    ${ADB_ID}
    Sleep    1s
    generic.Check USB Picture    ${CAMERA_INDEX}
    generic.Route Carlauncher    ${ADB_ID}

Audio 1kHz
    [Documentation]    Test audio with 1000khz sound
    generic.Route Files    ${ADB_ID}
    qvta.Open Audio in USB    ${ADB_ID}
    Wait Until Keyword Succeeds    30s    1s    generic.Check 1Hz Audio
    generic.Route Carlauncher    ${ADB_ID}