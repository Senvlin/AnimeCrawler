import html
import re
import urllib.parse
from base64 import b64decode


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


def base64_decode(string: str) -> str:
    '''对base64.b64decode()的包装

    Arguments:
        string -- 要解码的字符串

    Returns:
        解码后的字符串
    '''
    byte = bytes(string, 'utf-8')
    string = b64decode(byte).decode()
    return string


def unescape(string) -> str:
    '''对html.unescape()的包装

    Arguments:
        string -- 要解码的字符串

    Returns
        解码后的字符串'''
    string = urllib.parse.unquote(string)
    quoted = html.unescape(string).encode().decode('utf-8')
    # 转成中文
    return re.sub(
        r'%u([a-fA-F0-9]{4}|[a-fA-F0-9]{2})',
        lambda m: chr(int(m.group(1), 16)),
        quoted,
    )
