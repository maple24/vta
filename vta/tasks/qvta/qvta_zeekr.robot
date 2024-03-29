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
${server}    https://hw-snc-jfrog-dmz.zeekrlife.com/artifactory/
${repo}    zeekr/8295_ZEEKR/daily_cx1e/
${pattern}    qfil_.*
@{dunder}    bosch-gitauto    Bosch-gitauto@123
${mail_subject}    [QVTa Report] ${repo}


*** Keywords ***
Download From Artifactory
    [Documentation]    download latest version from artifactory and unzip
    [Arguments]    ${url}=${None}
    IF    $url == $None
        ${source}    ArtifaHelper.Get Latest
        Should Not Be Equal As Strings    ${source}    ${None}    Fail to get latest version!
        ${url}    Set Variable    ${source}[url]
    END
    ${artifact} =  Evaluate  os.path.basename($url)
    Set Suite Variable    ${artifact}
    ${package}    ArtifaHelper.Download    ${url}
    File Should Exist    ${package}    File not exist!
    ${checksum}    ArtifaHelper.Checksum    ${package}    ${source}[sha1]
    Should Be True    ${checksum}    Checksum does not match!
    ArtifaHelper.Unzip    ${package}
    ${image}    ArtifaHelper.Get Swpath    name=all_images_8295
    Directory Should Exist    ${image}    Image directory does not exist!
    RETURN    ${image}
ZEEKR Login
    [Documentation]    login to zeekr system
    [Arguments]    ${adbid}
    GenericHelper.Prompt Command    adb -s ${adbid} shell input tap 820 1315
    GenericHelper.Prompt Command    adb -s ${adbid} shell input tap 1275 1430
    Sleep    2s
    GenericHelper.Prompt Command    adb -s ${adbid} shell input tap 1250 1430
    Sleep    3s
    GenericHelper.Prompt Command    adb -s ${adbid} shell input tap 1275 1430
    Sleep    3s
    GenericHelper.Prompt Command    adb -s ${adbid} shell input tap 1450 985
ZEEKR Recovery Mode
    [Arguments]    ${adbid}
    generic.Route EngineeringMode    ${adbid}
    Sleep    1s
    GenericHelper.Prompt Command    adb -s ${adbid} shell input tap 730 190
    Sleep    1s
    GenericHelper.Prompt Command    adb -s ${adbid} shell input tap 2455 275
Check ZEEKR SWUP Success
    [Arguments]    ${SWUP_timeout}    ${cameraindex}    ${adbid}
    Wait Until Keyword Succeeds    ${SWUP_timeout}    5 sec    Check Normal Mode and Thermal
    Sleep    10s
    ZEEKR Login    ${adbid}
    Wait Until Keyword Succeeds    2 minutes    5 sec    generic.Check Android Home and Thermal    ${cameraindex}


*** Test Cases ***
SWUP
    [Documentation]    Software upgrade
    ${image_path}    Download From Artifactory    url=${None}
    generic.UDisk to PC
    ${udisk}    GenericHelper.Get Removable Drives
    Remove Directory    ${udisk}//${image_name}    recursive=${True}
    Move Directory    ${image_path}    ${udisk}//${image_name}
    generic.UDisk to DHU
    ZEEKR Recovery Mode    ${ADB_ID}
    Check ZEEKR SWUP Success    ${SWUP_timeout}    ${CAMERA_INDEX}    ${ADB_ID}

Get Version
    [Documentation]    Get soc version
    ${SOCVersion}    qvta.Get SOC Version
    Set Suite Variable    ${SOCVersion}