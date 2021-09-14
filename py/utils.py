from urllib import parse
from typing import Any
import uuid
from browser.html import *
from browser import doc, window, timer

from py.common_utils import *
jq = window.jQuery
# window.firebase.auth().onAuthStateChanged(lambda user:window.location.reload())


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


def show_alert_message(
        message: str,
        fade_in_ms: int = 100,
        fade_delay_ms: int = 1500,
        fade_out_ms: int = 400,):
    """ 顯示淡出淡入訊息

    Ref:
        https://codepen.io/sunny_mody/pen/tJloA

    Args:
        message (str): 文字訊息
        fade_in_ms (int, optional): 淡入毫秒數. Defaults to 100.
        fade_delay_ms (int, optional): 訊息持續毫秒數. Defaults to 1500.
        fade_out_ms (int, optional): 淡出毫秒數. Defaults to 400.
    """
    def del_div(div_id):
        """ 刪除指定的 div
        """
        del doc[div_id]

    # 置入訊息 DIV 元素
    div_id = str(uuid.uuid4())
    doc <= DIV(
        message,
        id=div_id,
        style=dict(
            padding='15px',
            marginBottom='20px',
            border='1px solid transparent',
            borderRadius='4px',
            color='#3c763d',
            backgroundColor='#dff0d8',
            borderColor='#d6e9c6',
            display='none',
            zIndex="100",  # 最上層
            # 置中位置
            position="fixed",
            top="40%",
            width="100%",
        )
    )

    # 淡入淡出訊息
    jq(f'#{div_id}')\
        .fadeIn(fade_in_ms)\
        .delay(fade_delay_ms)\
        .fadeOut(fade_out_ms)

    # 刪除訊息 DIV 元素
    timer.set_timeout(
        del_div, (fade_in_ms+fade_delay_ms+fade_out_ms), div_id
    )
