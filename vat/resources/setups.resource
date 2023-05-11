*** Settings ***
Library    ../library/PuttyHelper.py    WITH NAME    mputty
Library    ../library/GenericHelper.py    WITH NAME    mgeneric
Library    ../library/DBHelper.py    WITH NAME    mdb
Variables    ../conf/base.py


*** Keywords ***
INIT
    [Documentation]    Init all instances
    mputty.Connect    dPutty=${dputty}


DEINIT
    [Documentation]    Deinit all instances
    mputty.Disconnect