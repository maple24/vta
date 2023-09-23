from he import PeriodicReleaseChecker
import os
import schedule


if __name__ == "__main__":
    ROOT = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-2])
    artifacts = [
        {
            "repo": "zeekr-dhu-repos/builds/rb-zeekr-dhu_hqx424-pcs01_main_binary/daily/",
            "pattern": "_userdebug_binary.tgz$",
        },
        {
            "repo": "zeekr-dhu-repos/builds/rb-zeekr-dhu_hqx424-pcs01_main_dev/daily/",
            "pattern": "_userdebug.tgz$",
        },
        {
            # "server": "https://rb-cmbinex-fe-p1.de.bosch.com/artifactory/",
            "repo": "zeekr-dhu-repos/builds/rb-zeekr-dhu_hqx424-pcs01_main_dev_zeekr_dhu_r1_release/daily/",
            "pattern": "_userdebug.tgz$",
        },
        {
            # "server": "https://rb-cmbinex-fe-p1.de.bosch.com/artifactory/",
            "repo": "zeekr-dhu-repos/builds/rb-zeekr-dhu_hqx424-pcs01_main_binary_zeekr_dhu_r1_release/daily/",
            "pattern": "_userdebug_binary.tgz$",
        },
    ]
    scripts = [
        os.path.join(ROOT, "QVTa_binary.bat"),
        os.path.join(ROOT, "QVTa_source.bat"),
        os.path.join(ROOT, "QVTa_release_source.bat"),
        os.path.join(ROOT, "QVTa_release_binary.bat"),
    ]
    release_checker = PeriodicReleaseChecker()
    release_checker.periodic_job(artifacts=artifacts, scripts=scripts)
    schedule.every(5).minutes.do(
        release_checker.periodic_job, artifacts=artifacts, scripts=scripts
    )
    # threading.Thread(target=release_checker.run_scheduler).start()
    release_checker.run_scheduler()
