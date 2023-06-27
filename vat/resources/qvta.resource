*** Settings ***
Library    ../api/PuttyHelper.py
Library    ../api/RelayHelper.py
Library    ../library/GenericHelper.py
Library    ../api/ArtifaHelper.py    zeekr-dhu-repos/builds/rb-zeekr-dhu_hqx424-fc_main_dev/daily/    _userdebug.tgz$
Library    OperatingSystem

*** Keywords ***
Download_Latest
    [Documentation]    download latest version from artifactory and unzip

    ${source}    ArtifaHelper.Get Latest
    Should Not Be Equal As Strings    ${source}    ${None}    Fail to get latest version!
    ${package}    ArtifaHelper.Download    ${source}[url]
    File Should Exist    ${package}    File not exist!
    ArtifaHelper.Unzip    ${package}
    ${image}    ArtifaHelper.Get Swpath    name=all_images_8295
    Directory Should Exist    ${image}    Image directory does not exist!

    RETURN    ${image}
Open_DMS
    PuttyHelper.Send Command    /mnt/bin/camera/qcarcam_test/qcarcam_test -config=dms_test.xml
Open_OMS
    PuttyHelper.Send Command    /mnt/bin/camera/qcarcam_test/qcarcam_test -config=oms1_test.xml
Open_Backlight
    PuttyHelper.Send Command    sw-vsync -display=5
ADB_Enable
    # mount usb2.0 to android
    PuttyHelper.Send Command    bosch_swdl_assistant -o "{\"type\":\"usb_owner\", \"port\":0, \"owner\":3, \"io\":2}"
    # reset
    PuttyHelper.Send Command    bosch reset
CheckDLT
    # MCU reset reason