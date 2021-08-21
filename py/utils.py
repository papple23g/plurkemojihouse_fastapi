from urllib import parse

from py.common_utils import *


def get_url_query_dict(url: str) -> dict:
    """ 獲取 URL 的請求參數字典

    Args:
        url (str)

    Returns:
        dict

    Ref:
        https://stackoverflow.com/a/21584580/5269826
    """
    return dict(parse.parse_qsl(parse.urlsplit(url).query))
