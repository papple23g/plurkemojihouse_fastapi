from io import BytesIO
import imagehash
from PIL import Image  # python -m pip install Pillow
import requests
from typing import List


def is_alive_url(url: str) -> bool:
    """ 網址是否存在

    Args:
        url (str): 網址

    Returns:
        bool
    """
    res = requests.head(url)
    return (res.status_code == 200)


def get_average_hash(img_src: str) -> str:
    """ 根據圖片網址獲取平均哈希值

    Args:
        img_src (str): 圖片網址

    Returns:
        str
    """
    img_res = requests.get(img_src)
    image = Image.open(BytesIO(img_res.content))
    return str(imagehash.average_hash(image))


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


if __name__ == '__main__':
    print(type(average_hash('https://i.imgur.com/Mv3fvJ0.j')))
