*** Settings ***
Resource    ../resources/generic.resource
Resource    ../resources/swup.resource
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
SWUP Execution
    [Documentation]    randomly select software package and run test
    ${keyword_list}    Create List    USB0    USB1
    generic.Randomly Run Keywords    ${keyword_list}
    swup.Enter Recovery Mode
    swup.Check SWUP Success    ${SWUP_timeout}
