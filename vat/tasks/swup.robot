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
${image}    all_images

*** Keywords ***
USB0
    RelayHelper.Set Relay Port    dev_type=multiplexer    port_index=13
    Sleep    1s

USB1
    RelayHelper.Set Relay Port    dev_type=multiplexer    port_index=14
    Sleep    1s

CheckImage
    ${udisk}    GenericHelper.Get Removable Drives
    Directory Should Exist    ${udisk}//${image}    Software package not found!
CheckLog
    

*** Test Cases ***
SWUP
    ${seed}    Generate Random String    1    01
    Run Keyword If    ${seed}==0    USB0
    Run Keyword If    ${seed}==1    USB1
    CheckImage
    swup.RecoveryMode
    swup.TrigerUpgrade