import html
import re
import urllib.parse
from base64 import b64decode


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


def folder_path(folder_path):
    print(f'{folder_path=}')

    if not folder_path.exists():
        folder_path.mkdir()
    return folder_path
