SLOT_1_POWERCYCLE = {
    "steps": {
        "StepTest": {"enabled": True, "name": "maple"},
        "StepCheckPowerCycle": {"enabled": True, "type": "network"},
        "CheckStartupTrace": {"enabled": False},
        "StepCheckRamdump": {"enabled": False},
        "StepCheckCrash": {
            "enabled": False,
            "ex_filters": [],
            "stop_filters": ["audio_service.core"],
        },
        "StepCheckProcesses": {"enabled": False, "qvm": "tmp/linux-la.config"},
        "StepCheckLogdataStatus": {"enabled": False},
        "StepCheckDisplays": {
            "enabled": True,
            "displays": [
                {"index": 1, "profile": "Android_Home"},
                {"index": 0, "profile": "Beantech_Home"},
                {"index": 0, "profile": "Cluster"},
            ],
        },
    }
}
