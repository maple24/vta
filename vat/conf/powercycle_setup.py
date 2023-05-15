SLOT_1_POWERCYCLE = {
    "keywords_hook": ["StepTest", "StepCheckRamdump", "StepCheckProcesses", "StepCheckDisplays"],
    "steps": {
        "StepTest": {"enabled": True, "args": {"name": "maple"}},
        "StepPowerCycle": {
            "enabled": True,
            "args": {
                "scenario": "network",
                "off_wait": 10,
                "on_wait": 60,
                "sleep_check": "trace",
                "sleeptimeout": 180,
            },
        },
        "StepCheckResetTrace": {"enabled": False, "args": {}},
        "StepCheckRamdump": {"enabled": False, "args": {}},
        "StepCheckCrash": {
            "enabled": False,
            "args": {"ex_filters": [], "stop_filters": ["audio_service.core"]},
        },
        "StepCheckProcesses": {"enabled": False, "args": {"qvm": "tmp/linux-la.config"}},
        "StepCheckLogdataStatus": {"enabled": False, "args": {}},
        "StepCheckDisplays": {
            "enabled": True,
            "args": {
                "android_display": {
                    "enabledd": True,
                    "index": 1,
                    "profile": "Beantech_Home",
                },
                "cluster_display": {
                    "enabledd": False,
                    "index": 1,
                    "profile": "Cluster_Home_v71",
                },
                "cp_display": {"enabledd": False, "index": 1, "profile": "CP_Home"},
            },
        },
    },
}
