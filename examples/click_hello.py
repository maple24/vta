import click
from typing import Optional


class Config:
    def __init__(self) -> None:
        self.verbose: bool = False
        self.home_directory: Optional[str] = None


pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group()
@click.option("--verbose", is_flag=True, help="Enable verbose mode.")
@click.option("--home-directory", type=click.Path(), help="Specify the home directory.")
@pass_config
def cli(config: Config, verbose: bool, home_directory: Optional[str]) -> None:
    """Main CLI entry point."""
    config.verbose = verbose
    if home_directory is None:
        home_directory = "."
    config.home_directory = home_directory


@cli.command()
@click.option("--string", default="World", help="The string to greet.")
@click.option("--repeat", default=1, help="Number of times to greet.")
@click.argument("out", type=click.File("w"), default="-", required=False)
@pass_config
def say(config: Config, string: str, repeat: int, out) -> None:
    """Greet with a message."""
    if config.verbose:
        click.echo("Verbose mode is on.")
    click.echo(f"Home directory: {config.home_directory}")
    for _ in range(repeat):
        click.echo(f"Hello {string}", file=out)


if __name__ == "__main__":
    cli()
