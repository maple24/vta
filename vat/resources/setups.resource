*** Settings ***
Library    ../library/PuttyHelper.py
Library    ../library/GenericHelper.py
Library    ../api/TSmasterAPI/TSClient.py
Resource    ../resources/generic.resource


*** Keywords ***
INIT
    [Documentation]    Init all instances
    [Arguments]    ${CONF}
    PuttyHelper.Connect    dPutty=${CONF}[dputty]
    PuttyHelper.Enable Monitor

    TSClient.Init Tsmaster    ${CONF}[dtsmaster]
    TSClient.Start Simulation
    DefineGlobal

DEINIT
    [Documentation]    Deinit all instances
    PuttyHelper.Disconnect
    PuttyHelper.Disable Monitor

    TSClient.Stop Simulation

DefineGlobal
    [Documentation]    Define global variables
    ${TESTER}    GenericHelper.Get Username
    ${BENCHID}    GenericHelper.Get Hostname
    ${SOCVersion}    generic.GetSOCVersion
    # ${SCCVersion}    generic.GetSCCVersion
    Set Global Variable    ${TESTER}
    Set Global Variable    ${BENCHID}
    Set Global Variable    ${SOCVersion}
    # Set Global Variable    ${SCCVersion}