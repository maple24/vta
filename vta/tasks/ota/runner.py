import click
import sys
import json
import os
from pathlib import Path
from datetime import datetime
from loguru import logger
from vta.core.runner.utils import rotate_folder
from vta.api.TSmasterAPI.TSRPC import DeviceMode
from vta.tasks.ota.ota import OTAConfig, OTA
from typing import Dict, Any, Tuple
from vta.tasks.ota.reporting import TestReporter
from vta.core.mail.EMAILClient import EmailClient, EmailClientError

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
    
    # Generate console and HTML reports
    ota_reporter.generate_console_report(results)
    html_summary_path = ota_reporter.generate_html_summary_report(results)
    
    # Send email report
    send_email_report(results, iterations, html_summary_path)


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
    # TODO
    config["tsmaster_config"]["dev_mode"] = getattr(DeviceMode, config["tsmaster_config"]["dev_mode"])
    return config


def send_email_report(results: list, total_iterations: int, html_report_path: Path = None) -> None:
    """Send email with test summary report"""
    try:
        config = load_config()
        email_config = config.get("email_config", {})
        
        if not email_config.get("enabled", False):
            logger.info("Email reporting is disabled")
            return
        
        if not all([email_config.get("sender"), email_config.get("username"), 
                    email_config.get("password"), email_config.get("recipients")]):
            logger.warning("Email configuration incomplete, skipping email report")
            return
        
        # Generate email content
        successful_tests = sum(1 for result in results if result["success"])
        test_status = "PASSED" if successful_tests == len(results) else "FAILED"
        
        # Create email subject
        subject = f"OTA Test Report - {test_status} ({successful_tests}/{total_iterations} iterations passed)"
        
        # Read the existing HTML summary report
        try:
            if html_report_path and html_report_path.exists():
                with open(html_report_path, 'r', encoding='utf-8') as f:
                    html_body = f.read()
                logger.info(f"Using HTML report from: {html_report_path}")
            else:
                logger.error("HTML summary report not found")
                return
        except Exception as e:
            logger.error(f"Failed to read HTML summary report: {e}")
            return
        
        # Initialize email client and send
        email_client = EmailClient(
            sender=email_config["sender"],
            username=email_config["username"],
            password=email_config["password"]
        )
        
        logger.info(f"Sending email report to: {', '.join(email_config['recipients'])}")
        email_client.send_mail(
            recipients=email_config["recipients"],
            subject=subject,
            email_body=html_body,
            content_type="html"
        )
        logger.success("Email report sent successfully")
            
    except EmailClientError as e:
        logger.error(f"Email client error: {e}")
    except Exception as e:
        logger.error(f"Failed to send email report: {e}")


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