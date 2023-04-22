import abc
import argparse
import re
from collections import namedtuple

from AnimeCrawler.log import get_logger
from AnimeCrawler.mhyyy.spider import AnimeSpider


class BaseCommand:
    '''命令的基类

    子类必须实现 subcommand_add_arguments， handle 方法
    '''

    logger = get_logger('Command')

    @abc.abstractmethod
    def subcommand_add_arguments(self, parser):
        ...

    @abc.abstractmethod
    def handle(self, args):
        ...


def is_url(string: str):
    '''解析是否为url

    Args:
        string (str): 要解析的字符串

    Returns:
        bool: 用于判断
    '''
    pattern = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$',
        re.IGNORECASE,
    )
    return bool(re.search(pattern, string))


class DownloadCommand(BaseCommand):
    def subcommand_add_arguments(self, parser: argparse._SubParsersAction):
        parser.add_argument(
            "-u",
            "--url",
            metavar='URL',
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
