""" 後端(fastapi) 與 前端(Brython) 共用的工具函數
"""

from typing import List


def tags_str_2_tag_str_list(tags_str: str) -> List[str]:
    """ 以逗號分隔的標籤字串，並去掉前後空白，且不會輸出空白字串

    Returns:
        List[str]
    """
    tag_str_list = [
        tag_str.replace('　', ' ').strip()
        for tag_str in tags_str.split(',')
    ]
    return [
        tag_str for tag_str in tag_str_list if tag_str
    ]
