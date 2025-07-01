import click
from rich.console import Console
from rich.table import Table
from loguru import logger
from vta.tasks.ota.ota import OTA

console = Console()


@click.command()
@click.option("--iterations", prompt="Enter the number of iterations for the OTA test", type=int)
def main(iterations):
    results = []

    for i in range(iterations):
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
            skip_download=True,
            skip_slot_check=True,
            skip_trigger_upgrade=True,
            skip_upgrade_monitor=True,
        )
        results.append(test_result)

        if test_result:
            logger.success(f"Iteration {i + 1} completed successfully")
        else:
            logger.error(f"Iteration {i + 1} failed")

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
