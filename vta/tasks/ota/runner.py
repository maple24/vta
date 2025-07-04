import click
import sys
from pathlib import Path
from datetime import datetime
from loguru import logger
from vta.core.runner.utils import rotate_folder
from vta.api.TSmasterAPI.TSRPC import DeviceMode
from vta.tasks.ota.ota import OTAConfig, OTA
from typing import Dict, Any, List, Tuple
from vta.tasks.ota.reporting import TestReporter

ROOT = Path(__file__).resolve().parent.parent.parent.parent
LOG_PATH = ROOT / "log" / datetime.now().strftime("%A_%m%d%Y_%H%M")
LOG_PATH.mkdir(parents=True, exist_ok=True)
# Create default OTA reporter instance
_ota_reporter = TestReporter("OTA Test")


def generate_html_report_for_iteration(
    iteration_num: int, success: bool, runtime: float, failing_steps: str, log_path: Path
) -> Path:
    """Backward compatibility wrapper"""
    return _ota_reporter.generate_html_report_for_iteration(iteration_num, success, runtime, failing_steps, log_path)


def generate_html_summary_report(results: List[Dict[str, Any]]) -> Path:
    """Backward compatibility wrapper"""
    return _ota_reporter.generate_html_summary_report(results)


def generate_report(results: List[Dict[str, Any]]) -> None:
    """Backward compatibility wrapper"""
    _ota_reporter.generate_console_report(results)


@click.command()
@click.option("--iterations", prompt="Enter the number of iterations for the OTA test", type=int)
def main(iterations: int) -> None:
    results = []
    for i in range(iterations):
        result_entry, test_result = run_iteration(i, iterations)
        results.append(result_entry)
        if not test_result:
            break
    generate_report(results)
    generate_html_summary_report(results)


def setup_logger(iteration: int) -> Path:
    logger.remove()
    logger.add(sys.stdout, level="DEBUG")
    iteration_log_path = LOG_PATH / f"log_iter_{iteration + 1}_{datetime.now().strftime('%m%d%Y_%H%M%S')}.log"
    logger.add(
        str(iteration_log_path),
        backtrace=True,
        diagnose=False,
        format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
        rotation="1 week",
        level="TRACE",
    )
    rotate_folder(ROOT / "log")
    return iteration_log_path


def run_iteration(i: int, total_iterations: int) -> Tuple[Dict[str, Any], bool]:
    iteration_log_path = setup_logger(i)
    logger.info(f"Starting iteration {i + 1} of {total_iterations}")

    # Setup OTA configuration
    putty_config = {
        "putty_enabled": True,
        "putty_comport": "COM44",
        "putty_baudrate": 921600,
        "putty_username": "",
        "putty_password": "",
    }
    device_id = "2801750c52300030"
    tsmaster_config = {"app_name": "TSMaster", "dev_mode": DeviceMode.CAN, "auto_start_simulation": True}
    ota_config = OTAConfig(putty_config=putty_config, tsmaster_config=tsmaster_config, device_id=device_id)

    start_time = datetime.now()
    try:
        with OTA(ota_config) as ota:
            test_result = ota.perform_ota_test(
                skip_download=False,
                skip_slot_check=False,
                skip_trigger_upgrade=False,
                skip_upgrade_monitor=False,
            )
    except Exception as e:
        test_result = False
        error_message = str(e)
        logger.error(f"Iteration {i + 1} encountered an error: {error_message}")
        failing_steps = f"Test encountered error: {error_message}"
    else:
        failing_steps = "" if test_result else "Check OTA logs for details"
    duration = (datetime.now() - start_time).total_seconds()

    result_entry = {"iteration": i + 1, "success": test_result, "runtime": duration, "failing_steps": failing_steps}
    html_report_path = generate_html_report_for_iteration(
        i + 1, test_result, duration, failing_steps, iteration_log_path
    )
    logger.info(f"HTML report for iteration {i + 1} generated: {html_report_path}")
    if test_result:
        logger.success(f"Iteration {i + 1} completed successfully")
    else:
        logger.error(f"Iteration {i + 1} failed")
        logger.error("Stopping iterations due to failure")
    return result_entry, test_result


if __name__ == "__main__":
    main()
