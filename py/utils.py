from urllib import parse
from browser import doc
from browser.html import TEXTAREA

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


def copy_text_to_cliboard(text: str) -> None:
    """ 將文字複製到剪貼簿
    """
    # 暫時建立一個文字區域
    textarea_id = 'temp_copy_text_to_cliboard_textarea'
    doc <= TEXTAREA(text, id=textarea_id)
    # 選定該元素
    doc[textarea_id].select()
    # 執行複製的動作
    doc.execCommand('copy')
    # 刪除文字區域元素
    del doc[textarea_id]
