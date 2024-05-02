import asyncio

import click

from zuna.src.config import Config
from zuna.src.engine import Engine
from zuna.src.query import Query

cfg = Config()

@click.group()
@click.version_option(
    version="0.1.0",
    prog_name="Zuna",
    message="%(prog)s [v%(version)s] - A simple anime downloader",
)
def cli(): ...

@cli.command(help="Search for anime")
@click.option("-n", "--anime_name", help="The name of the anime", required=True)
def search(anime_name):
    query = Query()
    asyncio.run(query.search(anime_name))
    query.pretty_print()

@cli.command(help="Download anime from the given url")
@click.option(
    "-u",
    "--root_url",
    help="The anime url to start scraping from",
    required=True,
)
@click.option("-n", "--anime_name", help="The name of the anime", required=True)
def download(root_url, anime_name):
    engine = Engine()
    cfg.config["common"]["anime_name"] = anime_name
    asyncio.run(engine.run(root_url))


@cli.command(help="Configure the program")
@click.option(
    "--log_level", type=str, help="The log level to use", default="INFO"
)
@click.option(
    "--max_concurrent_requests",
    type=click.IntRange(1, 32),
    help="The maximum number of concurrent requests",
    default=16,
)
def config(log_level, max_concurrent_requests):

    if log_level not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
        raise click.BadParameter("Invalid log level")
    cfg.config["common"]["log_level"] = log_level
    cfg.config["download"]["max_concurrent_requests"] = str(
        max_concurrent_requests
    )

if __name__ == "__main__":
    cli()
