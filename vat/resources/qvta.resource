*** Settings ***
Library    ../api/PuttyHelper.py
Library    ../api/RelayHelper.py
Library    ../library/GenericHelper.py

*** Keywords ***
Putty_CtrlC
    PuttyHelper.Send Command    \x03
Open_DMS
    PuttyHelper.Send Command    /mnt/bin/camera/qcarcam_test/qcarcam_test -config=dms_test.xml
Open_OMS
    PuttyHelper.Send Command    /mnt/bin/camera/qcarcam_test/qcarcam_test -config=oms1_test.xml
Open_Backlight
    PuttyHelper.Send Command    sw-vsync -display=5
ACC_ON
    RelayHelper.Set Relay Port    dev_type=xinke    port_index=2    state_code=0
ACC_OFF
    RelayHelper.Set Relay Port    dev_type=xinke    port_index=2    state_code=1
Route_Carlauncher
    GenericHelper.Prompt Command    adb shell am start com.android.car.carlauncher/.CarLauncher
ADB_Enable
    # mount usb2.0 to android
    PuttyHelper.Send Command    bosch_swdl_assistant -o "{\"type\":\"usb_owner\", \"port\":0, \"owner\":3, \"io\":2}"
    # reset
    PuttyHelper.Send Command    bosch reset

UDisk2PC
    RelayHelper.Set Relay Port    dev_type=multiplexer    port_index=14

UDisk2DHU
    RelayHelper.Set Relay Port    dev_type=multiplexer    port_index=24
CheckDLT
    # MCU reset reason