*** Settings ***
Library    ../library/PuttyHelper.py    WITH NAME    mputty
Library    ../library/GenericHelper.py    WITH NAME    mgeneric
Library    ../library/DBHelper.py    WITH NAME    mdb


*** Keywords ***
INIT
    [Documentation]    Init all instances
    [Arguments]    ${SLOT}

    mputty.Connect    dPutty=${SLOT}[dputty]


DEINIT
    [Documentation]    Deinit all instances
    mputty.Disconnect