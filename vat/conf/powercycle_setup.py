SLOT1 = {
    "max_test_iterations": 2000,
    "keywords_hook": ["GwmStepCheckRamdump",
                        "GwmStepCheckProcesses",
                        "GwmStepCheckDisplays"
    ],
    
    "keywords_seq": [
        "GwmStepPowerCycle",
        "GwmStepCheckSocVersion",
        "GwmStepCheckRamdump",
        "GwmStepCheckStartupCrash",
        "GwmStepCheckResetTrace",
        "GwmStepCheckProcesses",
        "GwmStepCheckLogdataStatus",
        "GwmStepCheckDisplays"
    ],
    "steps": {
        "GwmStepPowerCycle": {
            "state": "True",
            "arguments": {
                "scenario": "network",

                "current_thres": 0.1,
                "off_wait": 10,
                "on_wait": 60,
                "sleep_check": "trace",

                "sleeptimeout": 180
            }
        },
        "GwmStepCheckSocVersion": {
            "state": "True",
            "arguments": {
                "target_ver": "BUX2201.107.userdebug"
            }
        },
        "GwmStepCheckResetTrace": {
            "state": "True",
            "arguments": {
                
            }
        },
        "GwmStepCheckRamdump": {
            "state": "True",
            "arguments": {
                
            }
        },
        "GwmStepCheckStartupCrash": {
            "state": "True",
            "arguments": {
                "ex_filters": [
                
                ],
                "stop_filters": [
                    "audio_service.core"
                ]
            }
        },
        "GwmStepCheckProcesses":{
        "state":"True",
        "arguments":{
            "qvm":"tmp/linux-la.config"
            }
        },
        "GwmStepCheckLogdataStatus":{
        "state":"True",
        "arguments": {
        
            }
        },
        "GwmStepCheckDisplays": {
            "state": "True",
            "arguments": {
                "android_display": {
                    "enabled": "True",
                    "index": 1,
                    "profile": "Beantech_Home"
                },
                "cluster_display": {
                    "enabled": "False",
                    "index": 1,
                    "profile": "Cluster_Home_v71"
                },
                "cp_display": {
                    "enabled": "False",
                    "index": 1,
                    "profile": "CP_Home"
                }
            }
        }
    }
}
