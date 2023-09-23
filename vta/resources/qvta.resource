*** Settings ***
Resource    ../resources/powercycle.resource
Library    ../api/PuttyHelper.py
Library    ../api/RelayHelper.py
Library    ../library/GenericHelper.py
Library    OperatingSystem

*** Keywords ***
Mount USB to Android
    [Arguments]    ${cameraindex}
    # mount usb2.0 to android
    PuttyHelper.Send Command And Return Traces    bosch_swdl_assistant -o "{\\"type\\":\\"usb_owner\\", \\"port\\":0, \\"owner\\":0, \\"io\\":2}"
    PuttyHelper.Send Command And Return Traces    sync    login=${False}
    powercycle.Reset by PPS    ${cameraindex}
Mount USB to QNX
    [Arguments]    ${cameraindex}
    PuttyHelper.Send Command And Return Traces    bosch_swdl_assistant -o "{\\"type\\":\\"usb_owner\\", \\"port\\":0, \\"owner\\":1, \\"io\\":2}"
    PuttyHelper.Send Command And Return Traces    sync    login=${False}
    powercycle.Reset by PPS    ${cameraindex}
Exit Camera
    PuttyHelper.Send Command And Return Traces    e    login=${False}
Open DMS
    PuttyHelper.Send Command And Return Traces    cd /mnt/bin/camera/qcarcam_test
    PuttyHelper.Send Command And Return Traces    ./qcarcam_test -config=dms_test.xml    login=${False}    wait=${1}
Open OMS
    PuttyHelper.Send Command And Return Traces    cd /mnt/bin/camera/qcarcam_test
    PuttyHelper.Send Command And Return Traces    ./qcarcam_test -config=oms1_test.xml    login=${False}    wait=${1}
Open Backlight
    PuttyHelper.Send Command And Return Traces    sw-vsync -display=5
Check DLT
    @{traces}=    DLTHelper.Get Trace Container
    ${RES}    ${matched}=    GenericHelper.Match String    (POWERM_SM_RUN_STATE)    ${traces}
    Should Be True    ${RES}    Fail to match pattern `POWERM_SM_RUN_STATE`!
Open Picture in USB
    [Arguments]    ${adbid}
    GenericHelper.Prompt Command    adb -s ${adbid} shell input tap 50 577
    GenericHelper.Prompt Command    adb -s ${adbid} shell input tap 540 500
Open Audio in USB
    [Arguments]    ${adbid}
    # select music player
    GenericHelper.Prompt Command    adb -s ${adbid} shell input tap 50 577
    GenericHelper.Prompt Command    adb -s ${adbid} shell input tap 370 500
    GenericHelper.Prompt Command    adb -s ${adbid} shell input tap 700 260
    GenericHelper.Prompt Command    adb -s ${adbid} shell input tap 2350 115
    # replay
    GenericHelper.Prompt Command    adb -s ${adbid} shell input tap 50 577
    GenericHelper.Prompt Command    adb -s ${adbid} shell input tap 370 500
Get SOC Version
    [Documentation]    Get SOC version with putty command 'cat buildinfo.txt'
    ${RES}    ${MATCHED}    PuttyHelper.Wait For Trace    pattern=MAIN_VERSION\=(.*)    cmd=cat /mnt/Buildinfo.txt    timeout=10
    Should Be True    ${RES}    Unable to get SOC version
    RETURN    ${MATCHED}[0]
Get SCC Version
    [Documentation]    Get SCC version with putty command 'swup_scc -i 1'
    ${RES}    ${MATCHED}    PuttyHelper.Wait For Trace    pattern=SCC FW Version Info: (.*)    cmd=swup_scc -i 1    timeout=10
    Should Be True    ${RES}    Unable to get SCC version
    RETURN    ${MATCHED}[0]