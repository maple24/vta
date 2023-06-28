*** Settings ***
Library    ../api/AgentHelper.py
Library    ../api/PuttyHelper.py
Library    ../api/CANoeHelper.py
Library    ../library/GenericHelper.py
Library    Collections

*** Keywords ***
Test
    [Documentation]    ...
    [Arguments]    ${name}
    Log To Console    ${name}
    Should Be Equal    123    1    force failure

Check Display
    [Documentation]    Check profile display using webcam, args: list
    [Arguments]    ${dispalys}
    FOR    ${element}    IN    @{dispalys}
        ${RES}    Run Keyword If    ${element}[index]!=${0}    AgentHelper.Req To Test Profile    ${element}[index]   ${element}[profile]
        Run Keyword If    ${RES}!=${None}    Should Be Equal    ${RES}    ${0}    Profile does not match!
    END

Check Crash
    [Documentation]    Check if crash happens
    [Arguments]    ${ex_filters}
    @{traces}=    PuttyHelper.Get Trace Container
    ${RES}    ${matched}=    GenericHelper.Match String    dumping to (.*)    ${traces}
    IF    ${RES} == ${False}    RETURN
    FOR    ${element}    IN    @{matched}
        List Should Contain Value    ${ex_filters}    ${element}[0]    Detect crash ${element}[0]!
    END

Check Normal Trace
    [Documentation]    Check trace from putty trace container
    [Arguments]    ${patterns}
    @{traces}    PuttyHelper.Get Trace Container
    FOR    ${element}    IN    @{patterns}
        ${RES}    ${matched}=    GenericHelper.Match String    ${element}    ${traces}
        Should Be Equal    ${RES}    ${True}    Trace not found! ${element}
    END

Check Error Trace
    [Documentation]    Inspect if ramdump trace pattern appeared in putty trace container
    [Arguments]    ${patterns}
    @{traces}    PuttyHelper.Get Trace Container
    FOR    ${element}    IN    @{patterns}
        ${RES}    ${matched}=    GenericHelper.Match String    ${element}    ${traces}
        Should Not Be Equal    ${RES}    ${True}    Error trace detected! ${element}
    END

Reset by CMD
    [Documentation]    Run powercycle with putty command 'bosch_reset'
    ${RES}    ${MATCHED}    PuttyHelper.Wait For Trace    pattern=(LCM Unmount is done successfully)    cmd=bosch_reset    timeout=30
    Should Be Equal    ${RES}    ${True}    Fail to get shutdown trace!
    Sleep    40s

GWM Reset by CAN
    [Documentation]    Run powercycle with can signals
    CANoeHelper.Init Canoe    enabled=${True}

    GWM_ShutdownbyCAN
    ${RES}    ${MATCHED}    PuttyHelper.Wait For Trace    pattern=(LCM killed)    timeout=30
    Should Be Equal    ${RES}    ${True}    Fail to get shutdown trace!

    GWM_StartupbyCAN
    ${RES}    ${MATCHED}    PuttyHelper.Wait For Trace    pattern=(Log Type: B)    timeout=60
    Should Be Equal    ${RES}    ${True}    Fail to get startup trace!

GWM Shutdown by CAN
    [Documentation]    Run powercycle with can signals
    &{IGOFF}    Create Dictionary    type=sys    namespace=IL    var=Ignition    value=0
    &{Sleep}    Create Dictionary    type=sys    namespace=NM_CAN1    var=Wakeup    value=0
    &{DoorClose}    Create Dictionary    type=signal    msg=BCM1    sig=DrvDoorSts    value=0    channel=1    bustype=CAN    
    &{DoorOpen}    Create Dictionary    type=signal    msg=BCM1    sig=DrvDoorSts    value=1    channel=1    bustype=CAN
    CANoeHelper.Set Can Variable    ${IGOFF}
    Sleep    0.1s
    CANoeHelper.Set Can Variable    ${DoorOpen}
    Sleep    0.1s
    CANoeHelper.Set Can Variable    ${DoorClose}
    Sleep    0.1s
    CANoeHelper.Set Can Variable    ${Sleep}

GWM Startup by CAN
    [Documentation]    ...
    &{IGON}    Create Dictionary    type=sys    namespace=IL    var=Ignition    value=2
    &{WakeUP}    Create Dictionary    type=sys    namespace=NM_CAN1    var=Wakeup    value=1
    CANoeHelper.Set Can Variable    ${IGON}
    CANoeHelper.Set Can Variable    ${WakeUP}