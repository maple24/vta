*** Settings ***
Resource    ../resources/generic.resource
Resource    ../resources/swup.resource
Resource    ../resources/qvta.resource
Library    String
Library    OperatingSystem
Library    ../api/RelayHelper.py
Library    ../library/GenericHelper.py
Variables    ../conf/settings.py

Suite Setup    generic.INIT    ${CONF_BASE}
Suite Teardown    generic.DEINIT

*** Variables ***
${SLOT}    SLOT_1
${CONF_BASE}    ${${SLOT}}
${image_name}    all_images
${SWUP_timeout}    30 minutes

*** Keywords ***
Mount
    PuttyHelper.Send Command And Return Traces    bosch_swdl_assistant -o "{\\"type\\":\\"usb_owner\\", \\"port\\":0, \\"owner\\":1, \\"io\\":2}"
    PuttyHelper.Send Command And Return Traces    sync    login=${False}
    powercycle.Reset by CMD
USB0
    RelayHelper.Set Relay Port    dev_type=cleware    port_index=1    state_code=1
    Sleep    1s
    swup.Check Image    ${image_name}
    RelayHelper.Set Relay Port    dev_type=cleware    port_index=5    state_code=1
    Sleep    1s
USB1
    RelayHelper.Set Relay Port    dev_type=cleware    port_index=2    state_code=1
    Sleep    1s
    swup.Check Image    ${image_name}
    RelayHelper.Set Relay Port    dev_type=cleware    port_index=6    state_code=1
    Sleep    1s

*** Test Cases ***
GetVersion
    ${SOCVersion}    qvta.Get SOC Version
    Set Suite Variable    ${SOCVersion}
SWUP Execution
    [Documentation]    randomly select software package and run test
    [Setup]    Run Keyword If    ${VIDEO}==${True}    generic.WebCam Video ON
    [Teardown]    Run Keyword If    ${VIDEO}==${True}    generic.WebCam Video OFF
    ${keyword_list}    Create List    USB0    USB1
    generic.Randomly Run Keywords    ${keyword_list}
    Mount
    swup.Enter Recovery Mode
    swup.Check SWUP Success    ${SWUP_timeout}
