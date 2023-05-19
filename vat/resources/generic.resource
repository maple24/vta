*** Settings ***
Library    ../library/PuttyHelper.py
Library    ../library/GenericHelper.py
Library    ../library/CANoeHelper.py
Library    GeventLibrary

*** Keywords ***
HelloWorld
    [Documentation]    helloworld
    Log To Console    helloworld
    
GetSOCVersion
    [Documentation]    Get SOC version with putty command 'cat buildinfo.txt'
    
    ${RES}    ${MATCHED}    PuttyHelper.Wait For Trace    pattern=MAIN_VERSION\=(.*)    cmd=cat Buildinfo.txt    timeout=10
    Should Be Equal    ${RES}    ${True}    Unable to get SOC version
    
    RETURN    ${MATCHED}

GetSCCVersion
    [Documentation]    Get SCC version with putty command 'swup_scc -i 1'

    ${RES}    ${MATCHED}    PuttyHelper.Wait For Trace    pattern=SCC FW Version Info: (.*)    cmd=swup_scc -i 1    timeout=10
    Should Be Equal    ${RES}    ${True}    Unable to get SCC version
    
    RETURN    ${MATCHED}

ResetbyCMD
    [Documentation]    Run powercycle with putty command 'bosch_reset'

    ${RES}    ${MATCHED}    PuttyHelper.Wait For Trace    pattern=(LCM Unmount is done successfully)    cmd=bosch_reset    timeout=10
    Should Be Equal    ${RES}    ${True}    Fail to get shutdown trace!
    Sleep    40s

GWM_ResetbyCAN
    [Documentation]    Run powercycle with can signals

    CANoeHelper.Init Canoe    enabled=${True}

    GWM_ShutdownbyCAN
    ${RES}    ${MATCHED}    PuttyHelper.Wait For Trace    pattern=(LCM Unmount is done successfully)    timeout=20
    Should Be Equal    ${RES}    ${True}    Fail to get shutdown trace!

    GWM_StartupbyCAN
    ${RES}    ${MATCHED}    PuttyHelper.Wait For Trace    pattern=(Startup complete)    timeout=30
    Should Be Equal    ${RES}    ${True}    Fail to get startup trace!

GWM_ShutdownbyCAN
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

GWM_StartupbyCAN
    [Documentation]    ...

    &{IGON}    Create Dictionary    type=sys    namespace=IL    var=Ignition    value=2
    &{WakeUP}    Create Dictionary    type=sys    namespace=NM_CAN1    var=Wakeup    value=1
    CANoeHelper.Set Can Variable    ${IGON}
    CANoeHelper.Set Can Variable    ${WakeUP}