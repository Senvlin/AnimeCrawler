import argparse
import re

from AnimeCrawler.mhyyy.spider import AnimeSpider


class CrawlerCommands:
    '''https://docs.python.org/zh-cn/3/library/argparse.html#quick-links-for-add-argument'''

    def is_url(self, string):
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

    def get_parser(self):
        parser = argparse.ArgumentParser(
            prog='AnimeCrawler',
            usage='%(prog)s <Commands> [Options]',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description='* AnimeCrawler v0.1.1 - 一个可免费下载动漫的爬虫\n* Repo: https://github.com/Senvlin/AnimeCrawler',
            epilog='Had Issues? Go To -> https://github.com/Senvlin/AnimeCrawler/issues',
            add_help=False,  # 在这里是为了自定义help文档所以禁用了
        )
        group1 = parser.add_argument_group('Commands', '主要命令')
        group1.add_argument('download', help="下载动漫", nargs='?', default=False)
        group1.add_argument('search', help="搜索动漫，未实现", action='store_true')
        group2 = parser.add_argument_group('Required', '必填参数')
        group2.add_argument("-t", "--title", metavar='Title', help="动漫名称")
        group3 = parser.add_argument_group('Options', '可选命令')
        group3.add_argument("-u", "--url", metavar='URL', help="动漫第一集的url")
        group3.add_argument(
            "--del_ts", dest='can_del_ts', help="删除ts文件", action='store_true'
        )
        group3.add_argument(
            "--test", dest='is_test', help="开启Test模式", action='store_true'
        )
        group3.add_argument("-h", dest='help', help="获取帮助，并退出程序", action='store_true')
        return parser

    def parse(self, test_list: list = None):
        parser = self.get_parser()
        parse = parser.parse_args(test_list)
        if parse.help:
            parser.print_help()
            parser.exit()
        if parse.download != 'download' and parse.search != 'search':
            if parse.is_test:
                return 'null_command'
            raise ValueError(f'无效的命令 {parse.download}')
        elif parse.search == 'search':
            if parse.is_test:
                return 'have not supported \'search\' command'
            raise NotImplementedError(f'未支持的命令 {parse.search}')
        elif parse.title is None:
            if parse.is_test:
                return 'null_title'
            raise ValueError(f'{parse.title} 为空')
        elif not self.is_url(parse.url):
            if parse.is_test:
                return 'is_not_url'
            raise ValueError(f'{parse.url} 不为合法的url')
        else:
            if parse.is_test:
                return 'OK'
            AnimeSpider.init(parse.title, parse.url, parse.can_del_ts).start()


def main():
    CrawlerCommands().parse()
