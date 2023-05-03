import abc
import argparse
from collections import namedtuple

from AnimeCrawler.log import get_logger
from AnimeCrawler.mhyyy.spider import AnimeSpider
from AnimeCrawler.utils import is_url


class BaseCommand:
    '''命令的基类

    子类必须实现 subcommand_add_arguments, handle, catch_error 方法
    '''

    logger = get_logger('Command')

    @abc.abstractmethod
    def subcommand_add_arguments(self, parser):
        ...

    @abc.abstractmethod
    def handle(self, args):
        ...

    @abc.abstractmethod
    def catch_error(self, parse):
        ...


class DownloadCommand(BaseCommand):
    def subcommand_add_arguments(self, parser: argparse._SubParsersAction):
        parser.add_argument(
            "-u",
            "--url",
            help="动漫第一集的url",
            required=True,
        )
        parser.add_argument(
            "-t",
            "--title",
            metavar='Title',
            help="动漫名称",
            required=True,
        )
        parser.add_argument(
            "--del_ts", dest='can_del_ts', help="删除ts文件", action='store_true'
        )

    def handle(self, args):
        if error := self.catch_error(args):
            self.logger.error(error.output)
        else:
            print(args.title, args.url)
            AnimeSpider.init(args.title, args.url, args.can_del_ts).start()

    def catch_error(self, parse):
        Errors = namedtuple("Errors", ('error_code', 'error_reason', 'output'))
        if not parse.title:
            return Errors('402', 'null_title', f'标题 {parse.title} 为空')
        elif not is_url(parse.url or ''):
            return Errors('403', 'is_not_url', f'{parse.url} 不为合法的url')


class SearchCommand(BaseCommand):
    def subcommand_add_arguments(self, parser):
        ...

    def handle(self, args):
        print(f'args = {args}')


def main():
    subcommands = {
        'download': (DownloadCommand, '下载动漫'),
        'search': (SearchCommand, '搜索动漫，未实现'),
    }
    parser = argparse.ArgumentParser(
        prog='AnimeCrawler',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='* AnimeCrawler v0.1.1 - 一个可免费下载动漫的爬虫\n* Repo: https://github.com/Senvlin/AnimeCrawler',
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
