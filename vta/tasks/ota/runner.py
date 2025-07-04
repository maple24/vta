import click
import sys
import json
from pathlib import Path
from datetime import datetime
from loguru import logger
from vta.core.runner.utils import rotate_folder
from vta.api.TSmasterAPI.TSRPC import DeviceMode
from vta.tasks.ota.ota import OTAConfig, OTA
from typing import Dict, Any, Tuple
from vta.tasks.ota.reporting import TestReporter

ROOT = Path(__file__).resolve().parent.parent.parent.parent
LOG_PATH = ROOT / "log" / datetime.now().strftime("%A_%m%d%Y_%H%M")
LOG_PATH.mkdir(parents=True, exist_ok=True)
# Create default OTA reporter instance
ota_reporter = TestReporter("OTA Test")


@click.command()
@click.option("--iterations", prompt="Enter the number of iterations for the OTA test", type=int)
def main(iterations: int) -> None:
    results = []
    for i in range(iterations):
        result_entry, test_result = run_iteration(i, iterations)
        results.append(result_entry)
        if not test_result:
            break
    ota_reporter.generate_console_report(results)
    ota_reporter.generate_html_summary_report(results)


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


def load_config() -> Dict[str, Any]:
    """Load configuration from JSON file"""
    config_path = Path(__file__).parent / "config.json"
    with open(config_path, "r") as f:
        config = json.load(f)

    # Convert string dev_mode to enum
    config["tsmaster_config"]["dev_mode"] = getattr(DeviceMode, config["tsmaster_config"]["dev_mode"])
    return config


def run_iteration(i: int, total_iterations: int) -> Tuple[Dict[str, Any], bool]:
    iteration_log_path = setup_logger(i)
    logger.info(f"Starting iteration {i + 1} of {total_iterations}")

    # Load configuration from JSON
    config = load_config()
    ota_config = OTAConfig(
        putty_config=config["putty_config"], tsmaster_config=config["tsmaster_config"], device_id=config["device_id"]
    )

    start_time = datetime.now()
    performance_metrics = {}
    failing_steps = ""
    
    try:
        with OTA(ota_config) as ota:
            test_result = ota.perform_ota_test(**config["ota_test_config"])
            
            # Capture performance metrics
            for metric in ["download_duration", "upgrade_duration"]:
                value = getattr(ota, metric, None)
                if value is not None:
                    performance_metrics[metric] = value
                    logger.success(f"{metric.replace('_', ' ').title()}: {value:.2f} seconds")
                
            failing_steps = "" if test_result else "Check OTA logs for details"
    except Exception as e:
        test_result = False
        error_message = str(e)
        logger.error(f"Iteration {i + 1} encountered an error: {error_message}")
        failing_steps = f"Test encountered error: {error_message}"
        
    duration = (datetime.now() - start_time).total_seconds()

    result_entry = {
        "iteration": i + 1, 
        "success": test_result, 
        "runtime": duration, 
        "failing_steps": failing_steps,
        **performance_metrics
    }
    
    # Pass performance metrics to individual iteration report
    html_report_path = ota_reporter.generate_html_report_for_iteration(
        i + 1, test_result, duration, failing_steps, iteration_log_path, performance_metrics
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
