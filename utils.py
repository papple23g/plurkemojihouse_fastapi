from io import BytesIO
import imagehash
from PIL import Image  # python -m pip install Pillow
import requests
from typing import List

from py.common_utils import *
import requests


def is_alive_url(url: str) -> bool:
    """ 網址是否存在

    Args:
        url (str): 網址

    Returns:
        bool
    """
    res = requests.head(url)
    return (res.status_code == 200)


def get_average_hash_str(img_src: str) -> str:
    """ 根據圖片網址獲取平均哈希值

    Args:
        img_src (str): 圖片網址

    Returns:
        str
    """
    img_res = requests.get(img_src)
    image = Image.open(BytesIO(img_res.content))
    return str(imagehash.average_hash(image))
