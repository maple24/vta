import click
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from loguru import logger
from vta.core.runner.utils import rotate_folder
from vta.api.TSmasterAPI.TSRPC import DeviceMode
from vta.tasks.ota.ota import OTAConfig
from vta.tasks.ota.ota import OTA
from datetime import datetime
from typing import List, Dict, Any, Tuple

ROOT = Path(__file__).resolve().parent.parent.parent.parent
LOG_PATH = ROOT / "log" / datetime.now().strftime("%A_%m%d%Y_%H%M")
LOG_PATH.mkdir(parents=True, exist_ok=True)

console = Console()


def generate_html_report_for_iteration(
    iteration_num: int, success: bool, runtime: float, failing_steps: str, log_path: Path
) -> Path:
    """Generate HTML report for a single iteration"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>OTA Test - Iteration {iteration_num}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background-color: #f0f0f0; padding: 10px; border-radius: 5px; }}
            .success {{ color: green; font-weight: bold; }}
            .failure {{ color: red; font-weight: bold; }}
            .metric {{ margin: 10px 0; }}
            .log-section {{ margin-top: 20px; background-color: #f9f9f9; padding: 10px; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>OTA Test Report - Iteration {iteration_num}</h1>
            <p>Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
        
        <div class="metric">
            <strong>Result:</strong> <span class="{"success" if success else "failure"}">
                {"PASS" if success else "FAIL"}
            </span>
        </div>
        
        <div class="metric">
            <strong>Runtime:</strong> {runtime:.2f} seconds
        </div>
        
        {'<div class="metric"><strong>Failing Steps:</strong> ' + failing_steps + "</div>" if failing_steps else ""}
        
        <div class="log-section">
            <h3>Log File Location</h3>
            <p>{log_path}</p>
        </div>
    </body>
    </html>
    """

    html_file_path = LOG_PATH / f"iteration_{iteration_num}_report.html"
    with open(html_file_path, "w") as f:
        f.write(html_content)

    return html_file_path


def generate_html_summary_report(results: List[Dict[str, Any]]) -> Path:
    """Generate HTML summary report for all iterations"""
    total_iterations = len(results)
    success_count = sum(1 for e in results if e["success"])
    failure_count = total_iterations - success_count
    avg_runtime = sum(e["runtime"] for e in results) / total_iterations if total_iterations > 0 else 0

    rows_html = ""
    for entry in results:
        status_class = "success" if entry["success"] else "failure"
        status_text = "PASS" if entry["success"] else "FAIL"
        rows_html += f"""
        <tr>
            <td>{entry["iteration"]}</td>
            <td class="{status_class}">{status_text}</td>
            <td>{entry["runtime"]:.2f}</td>
            <td>{entry["failing_steps"]}</td>
        </tr>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>OTA Test Summary Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background-color: #f0f0f0; padding: 10px; border-radius: 5px; }}
            .success {{ color: green; font-weight: bold; }}
            .failure {{ color: red; font-weight: bold; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .summary {{ background-color: #e6f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>OTA Test Summary Report</h1>
            <p>Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
        
        <div class="summary">
            <h2>Summary Statistics</h2>
            <p><strong>Total Iterations:</strong> {total_iterations}</p>
            <p><strong>Successful Tests:</strong> <span class="success">{success_count}</span></p>
            <p><strong>Failed Tests:</strong> <span class="failure">{failure_count}</span></p>
            <p><strong>Average Runtime:</strong> {avg_runtime:.2f} seconds</p>
            <p><strong>Success Rate:</strong> {(success_count / total_iterations * 100):.1f}%</p>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>Iteration</th>
                    <th>Result</th>
                    <th>Runtime (s)</th>
                    <th>Failing Steps</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </body>
    </html>
    """

    html_file_path = LOG_PATH / "summary_report.html"
    with open(html_file_path, "w") as f:
        f.write(html_content)

    logger.info(f"HTML summary report generated: {html_file_path}")
    return html_file_path


@click.command()
@click.option("--iterations", prompt="Enter the number of iterations for the OTA test", type=int)
def main(iterations: int) -> None:
    results = []

    for i in range(iterations):
        iteration_log_path = setup_logger(i)
        logger.info(f"Starting iteration {i + 1} of {iterations}")

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
        results.append(result_entry)

        # Generate HTML report for this iteration
        html_report_path = generate_html_report_for_iteration(
            i + 1, test_result, duration, failing_steps, iteration_log_path
        )
        logger.info(f"HTML report for iteration {i + 1} generated: {html_report_path}")
        if test_result:
            logger.success(f"Iteration {i + 1} completed successfully")
        else:
            logger.error(f"Iteration {i + 1} failed")
            logger.error("Stopping iterations due to failure")
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


def generate_report(results: List[Dict[str, Any]]) -> None:
    table = Table(title="OTA Test Report")
    table.add_column("Iteration", justify="center")
    table.add_column("Result", justify="center")
    table.add_column("Runtime (s)", justify="center")
    table.add_column("Failing Steps", justify="center")

    for entry in results:
        table.add_row(
            str(entry["iteration"]),
            "[green]PASS[/green]" if entry["success"] else "[red]FAIL[/red]",
            f"{entry['runtime']:.2f}",
            entry["failing_steps"],
        )

    # Calculate performance metrics.
    total_iterations = len(results)
    success_count = sum(1 for e in results if e["success"])
    failure_count = total_iterations - success_count
    avg_runtime = sum(e["runtime"] for e in results) / total_iterations if total_iterations > 0 else 0

    table.add_row("─" * 15, "─" * 15, "─" * 15, "─" * 15)
    table.add_row("[bold]Total Iterations[/bold]", str(total_iterations), "", "")
    table.add_row("[bold green]Total PASS[/bold green]", str(success_count), "", "")
    table.add_row("[bold red]Total FAIL[/bold red]", str(failure_count), "", "")
    table.add_row("[bold]Average Runtime (s)[/bold]", f"{avg_runtime:.2f}", "", "")

    console.print(table)


if __name__ == "__main__":
    main()
