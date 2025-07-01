import click
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from loguru import logger
from vta.core.runner.utils import rotate_folder
from vta.tasks.ota.ota import OTA
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent.parent.parent
LOG_PATH = ROOT / "log" / datetime.now().strftime('%A_%m%d%Y_%H%M')
LOG_PATH.mkdir(parents=True, exist_ok=True)

console = Console()

@click.command()
@click.option("--iterations", prompt="Enter the number of iterations for the OTA test", type=int)
def main(iterations):
    results = []

    for i in range(iterations):
        logger.remove()
        logger.add(sys.stdout, level="DEBUG")
        iteration_log_path = LOG_PATH / f"log_iter_{i+1}_{datetime.now().strftime('%m%d%Y_%H%M%S')}.log"
        logger.add(
            str(iteration_log_path),
            backtrace=True,
            diagnose=False,
            format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
            rotation="1 week",
            level="TRACE",
        )
        rotate_folder(ROOT / "log")
        logger.info(f"Starting iteration {i + 1} of {iterations}")

        putty_config = {
            "putty_enabled": True,
            "putty_comport": "COM44",
            "putty_baudrate": 921600,
            "putty_username": "",
            "putty_password": "",
        }
        device_id = "2801750c52300030"

        ota = OTA(putty_config=putty_config, device_id=device_id)
        test_result = ota.perform_ota_test(
            skip_download=False,
            skip_slot_check=False,
            skip_trigger_upgrade=False,
            skip_upgrade_monitor=False,
        )
        results.append(test_result)

        if test_result:
            logger.success(f"Iteration {i + 1} completed successfully")
        else:
            logger.error(f"Iteration {i + 1} failed")
        del ota

    generate_report(results)

def generate_report(results):
    success_count = results.count(True)
    failure_count = results.count(False)
    total_iterations = len(results)

    table = Table(title="OTA Test Report")
    table.add_column("Iteration", justify="center")
    table.add_column("Result", justify="center")

    for idx, result in enumerate(results, 1):
        table.add_row(str(idx), "[green]PASS[/green]" if result else "[red]FAIL[/red]")

    table.add_row("─" * 10, "─" * 10)
    table.add_row("[bold]Total[/bold]", str(total_iterations))
    table.add_row("[bold green]PASS[/bold green]", str(success_count))
    table.add_row("[bold red]FAIL[/bold red]", str(failure_count))

    console.print(table)

if __name__ == "__main__":
    main()