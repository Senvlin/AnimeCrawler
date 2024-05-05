import asyncio

import click

from src.config import Config
from src.engine import Engine
from src.item import AnimeItem
from src.query import Query

cfg: Config = Config()


@click.group()
@click.version_option(
    version="1.0.0",
    prog_name="Zuna",
    message="%(prog)s [v%(version)s] - A simple anime downloader",
)
def cli(): ...


@cli.command(help="Search for anime")
@click.argument("anime_name", type=str)
def search(anime_name):
    query: Query = Query()
    asyncio.run(query.search(anime_name))
    for fmt_result in query.format_result():
        click.echo(fmt_result)
    # 选择番剧
    index: int = click.prompt(
        "Please enter the number of the anime you want to download",
        type=click.IntRange(1, len(query.anime_list)),
    )
    anime: AnimeItem = query.select_anime(index)
    query.generate_download_command(anime)
    click.echo(
        f"Download command for {anime.name} has been created and copied to clipboard successfully"  # noqa: E501
    )


@cli.command(help="Download anime from the given url")
@click.option(
    "-u",
    "--root_url",
    help="The anime url to start scraping from",
    required=True,
)
@click.option("-n", "--anime_name", help="The name of the anime", required=True)
@click.option(
    "--del_ts",
    help="Delete the downloaded ts files after merging",
    is_flag=True,
)
def download(root_url, anime_name, del_ts):
    engine = Engine()
    cfg.config["common"]["anime_name"] = anime_name
    asyncio.run(engine.run(root_url, del_ts))


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
