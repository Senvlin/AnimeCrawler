import urllib.parse

from ruia import Request, Spider

from AnimeCrawler.log import get_logger
from AnimeCrawler.utils import is_url


class BaseSpider(Spider):
    '''所有爬虫的基类，必须提供domain与downloader属性

    Args:
        Spider (ruia.Spider): 继承于ruia框架的爬虫

    Raises:
        ValueError: 未定义domain时报错
        ValueError: 未定义downloader时报错

    Returns:
        cls: 为了链式调用ruia.Spider.start()
    '''

    logger = get_logger('Spider', 'WARNING')

    def __init__(self, *args, **spider_kwargs) -> None:
        super().__init__(*args, **spider_kwargs)
        if not hasattr(self, 'domain'):
            raise ValueError(f'{self.__class__.__name__} 未定义domain属性')
        elif not hasattr(self, 'downloader'):
            raise ValueError(f'{self.__class__.__name__} 未定义downloader下载器')

    @classmethod
    def init(cls):
        cls.start_urls = [
            i if is_url(i) else urllib.parse.urljoin(cls.domain, i)
            for i in cls.start_urls
        ]  # 当url为相对路径时与域名拼接
        return cls

    def urljoin(self, base, url, avoid_collision: bool = False) -> str:
        '''对urllib.parse.urljoin()的包装

        Args:
            base (str): 基础url
            url (str): 要拼接的url
            avoid_collision (bool, optional): 避免冲突，

            详情看：https://docs.python.org/zh-cn/3/library/urllib.parse.html#urllib.parse.urljoin

            Defaults to False.

        Returns:
            str: 拼接后的url
        '''
        if avoid_collision:
            url_parts = urllib.parse.urlsplit(url)
            url = urllib.parse.urlunsplit(url_parts._replace(scheme='', netloc=''))
        return urllib.parse.urljoin(base, url)

    async def follow(self, next_url: str = None, **kwargs) -> Request:
        '''爬取下一个页面

        Args:
            next_url (str, optional): 下一个url的相对路径. Defaults to None.

        Returns:
            ruia.Request: 可被yield
        '''
        return self.request(self.urljoin(self.domain, next_url), **kwargs)

    def get_domain(self, url: str) -> str:
        url_parts = urllib.parse.urlsplit(url)
        print(url)
        return '://'.join(url_parts[:2])  # e.g. https://docs.python.org/

    def get_path(self, url: str) -> str:
        url_parts = urllib.parse.urlsplit(url)
        return url_parts.path


if __name__ == '__main__':
    BaseSpider().get_domain(
        'https://docs.python.org/zh-cn/3/library/urllib.parse.html#urllib.parse.urljoin'
    )
