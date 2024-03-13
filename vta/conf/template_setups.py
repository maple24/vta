# ============================================================================================================
# C O P Y R I G H T
# ------------------------------------------------------------------------------------------------------------
# \copyright (C) 2024 Robert Bosch GmbH. All rights reserved.
# ============================================================================================================

SLOT_1_POWERCYCLE = {
    "steps": {
        "StepTest": {"enabled": True, "name": "maple"},
        "StepCheckPowerCycle": {"enabled": True, "type": "command"},
        "StepCheckOMS": {"enabled": True},
        "StepCheckDMS": {"enabled": True},
        "StepCheckNormalTrace": {"enabled": False, "patterns": ["(Log Type: B)"]},
        "StepCheckErrorTrace": {
            "enabled": False,
            "patterns": [
                "(XBLRamDump Image Loaded)",
            ],
        },
        "StepCheckCrash": {
            "enabled": False,
            "ex_filters": ["audio_service.core"],
        },
        "StepCheckDisplays": {
            "enabled": True,
            "displays": [
                {"index": 1, "profile": "Android_Home"},
                {"index": 0, "profile": "Beantech"},
                {"index": 0, "profile": "Cluster"},
            ],
        },
    }
}
