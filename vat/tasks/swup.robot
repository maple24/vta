*** Settings ***
Resource    ../resources/generic.resource
Resource    ../resources/swup.resource
Library    String
Library    OperatingSystem
Library    ../api/RelayHelper.py
Library    ../library/GenericHelper.py
Variables    ../conf/bench_setup.py

Suite Setup    generic.INIT    ${CONF_BASE}
Suite Teardown    generic.DEINIT

*** Variables ***
${SLOT}    SLOT_1
${CONF_BASE}    ${${SLOT}}
${image_name}    all_images

*** Keywords ***
USB0
    RelayHelper.Set Relay Port    dev_type=multiplexer    port_index=13
    Sleep    1s
USB1
    RelayHelper.Set Relay Port    dev_type=multiplexer    port_index=14
    Sleep    1s

*** Test Cases ***
SWUP Execution
    [Documentation]    randomly select software package and run test
    ${keyword_list}    Create List    USB0    USB1
    generic.Randomly Run Keywords    ${keyword_list}
    swup.Check Image    ${image_name}
    swup.Enter Recovery Mode
    swup.Triger Upgrade