import argparse
import re

from AnimeCrawler.mhyyy.spider import AnimeSpider


class CrawlerCommands:
    parser = argparse.ArgumentParser(
        prog='AnimeCrawler',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='* AnimeCrawler v0.1.0 - 一个可免费下载动漫的爬虫\n* Repo: https://github.com/Senvlin/AnimeCrawler',
        epilog='Had Issues? Go To -> https://github.com/Senvlin/AnimeCrawler/issues',
    )

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

    def parse(self):
        self.parser.add_argument("title", help="动漫名称")
        self.parser.add_argument("url", help="动漫第一集的url")
        parse = self.parser.parse_args()
        if parse.title is None:
            raise ValueError(f'{parse.title} 为空')
        if self.is_url(parse.url):
            AnimeSpider.init(parse.title, parse.url).start()
        else:
            raise ValueError(f'{parse.url} 不为合法的url')
