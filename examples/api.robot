*** Settings ***
Library             ../vat/api/TSmasterAPI/TSClient.py

*** Test Cases ***
API
    [Documentation]    ...
    &{dTSMaster}    Create Dictionary    tsmaster_enabled=${True}    tsmaster_rbs=123    tsmaster_channel_vgm=${0}    tsmaster_channel_vddm=${1}        
    TSClient.Init Tsmaster    ${dTSMaster}
    TSClient.Start Simulation
    TSClient.Set Signal    0/BackboneFR/CEM/CemBackBoneFr02/VehModMngtGlbSafe1UsgModSts    11
    TSClient.Set Signal    0/BackboneFR/CEM/CemBackBoneFr02/VehModMngtGlbSafe1_UB    1
    TSClient.Get Signal    0/BackboneFR/CEM/CemBackBoneFr02/VehModMngtGlbSafe1UsgModSts
    TSClient.Get Signal    0/BackboneFR/CEM/CemBackBoneFr02/VehModMngtGlbSafe1_UB
    TSClient.Stop Simulation