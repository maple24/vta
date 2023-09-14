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
${server}    https://hw-snc-jfrog-dmz.zeekrlife.com/artifactory/
${repo}    zeekr/8295_ZEEKR/daily_cx1e/
${pattern}    qfil_.*
@{dunder}    bosch-gitauto    Bosch-gitauto@123


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
    ${image_path}    Download From Artifactory    url=${None}
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