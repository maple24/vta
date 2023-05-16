*** Settings ***
Library    ../library/PuttyHelper.py
Library    ../library/GenericHelper.py


*** Keywords ***
INIT
    [Documentation]    Init all instances
    [Arguments]    ${SLOT}
    PuttyHelper.Connect    dPutty=${SLOT}[dputty]
    PuttyHelper.Enable Monitor


DEINIT
    [Documentation]    Deinit all instances
    [Arguments]    ${MESSAGE_CONTAINER}
    PuttyHelper.Disconnect
    PuttyHelper.Disable Monitor
    UploadData


UploadData
    [Documentation]    Update test result to database