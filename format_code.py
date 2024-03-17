import subprocess

from loguru import logger


def run_command(command):
    logger.info(f"Running command: {command}")
    process = subprocess.run(command.split(), capture_output=True, text=True)
    if process.returncode != 0:
        logger.error(f"Error occurred: {process.stderr}")
    else:
        logger.info(process.stdout)


def main():
    commands = [
        "black .",
        "flake8",
        "mypy .",
        "isort .",
    ]
    for command in commands:
        run_command(command)


if __name__ == "__main__":
    logger.add("format_script.log", rotation="500 MB", compression="zip", level="DEBUG")
    main()
