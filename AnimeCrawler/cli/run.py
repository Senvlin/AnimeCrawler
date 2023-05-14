import abc
import argparse
from collections import namedtuple

from AnimeCrawler.log import Logger
from AnimeCrawler.mhyyy.searcher import Searcher
from AnimeCrawler.mhyyy.spider import AnimeSpider
from AnimeCrawler.utils import is_url


class BaseCommand:
    '''命令的基类

    子类必须实现 subcommand_add_arguments, handle, catch_error 方法
    '''

    logger = Logger()

    @abc.abstractmethod
    def subcommand_add_arguments(self, parser) -> None:
        ...

    @abc.abstractmethod
    def handle(self, args) -> None:
        ...

    @property
    def base_error(self):
        Errors = namedtuple("Errors", ('error_code', 'error_reason', 'output'))
        return Errors


class DownloadCommand(BaseCommand):
    def subcommand_add_arguments(self, parser: argparse._SubParsersAction):
        parser.add_argument(
            "-u",
            "--url",
            help="动漫第一集的url",
        )
        parser.add_argument(
            "-t",
            "--title",
            metavar='Title',
            help="动漫名称",
        )
        parser.add_argument(
            "--del_ts", dest='can_del_ts', help="删除ts文件", action='store_true'
        )
        parser.add_argument(
            '--debug', dest='is_debug', help='进入debug模式', action='store_true'
        )

    def handle(self, args) -> None:
        if error := self.catch_error(args):
            raise ValueError(f'{error.output}')
        AnimeSpider.init(args.title, args.url, args.can_del_ts).start()

    def catch_error(self, parse):
        if not parse.title:
            return self.base_error('402', 'null_title', '标题为空')
        elif not is_url(parse.url or ''):
            return self.base_error('403', 'is_not_url', f'{parse.url} 不为合法的url')


class SearchCommand(BaseCommand):
    def subcommand_add_arguments(self, parser) -> None:
        parser.add_argument(
            "-t",
            "--title",
            metavar='Title',
            help="动漫名称",
        )
        parser.add_argument(
            '--debug', dest='is_debug', help='进入debug模式', action='store_true'
        )

    def handle(self, args) -> None:
        if error := self.catch_error(args):
            raise ValueError(f'{error.output}')
        Searcher.init(args.title, is_debug=args.is_debug).start()

    def catch_error(self, parse):
        if not parse.title:
            return self.base_error('402', 'null_title', '标题为空')


def main():
    subcommands = {
        'download': (DownloadCommand, '下载动漫'),
        'search': (SearchCommand, '搜索动漫'),
    }
    parser = argparse.ArgumentParser(
        prog='AnimeCrawler',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='* AnimeCrawler v0.2.0 - 一个可免费下载动漫的爬虫\n* Repo: https://github.com/Senvlin/AnimeCrawler',
        epilog='Had Issues? Go To -> https://github.com/Senvlin/AnimeCrawler/issues',
    )
    subparsers: argparse._SubParsersAction = parser.add_subparsers(prog='AnimeCrawler')
    for name, profile in subcommands.items():
        cmd: BaseCommand = profile[0]()
        subparser = subparsers.add_parser(name, help=profile[1])
        subparser.set_defaults(handle=cmd.handle)
        cmd.subcommand_add_arguments(subparser)
    args = parser.parse_args()
    if hasattr(args, 'handle'):
        args.handle(args)
