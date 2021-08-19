from pydantic import BaseModel, validator, root_validator
from typing import List
from uuid import UUID
import datetime
import imagehash


from utils import (
    is_alive_url,
    get_average_hash_str,
    tags_str_2_tag_str_list,
)


class OutBase(BaseModel):
    class Config:
        orm_mode = True


class IdOut(OutBase):
    id: UUID


class TagBase(BaseModel):
    id: UUID
    name: str


class TagOut(TagBase, OutBase):
    ...


class EmojiBase(BaseModel):
    url: str


class EmojiIn(EmojiBase):
    tags_str: str = None
    average_hash_str: str = None

    @validator('url')
    def format_url(url):
        """
        輸出前格式化:
        1. 去除中間空白與頭尾空白
        2. 一律使用 https 開頭
        """
        url = url.replace(' ', '').strip()
        if 'emos.plurk.com' in url:
            return "https://"+url[url.find('emos.plurk.com'):]
        elif 's.plurk.com' in url:
            return "https://"+url[url.find('s.plurk.com'):]
        else:
            raise ValueError(f'非噗浪表符網址: {url}')

    @validator('url')
    def alive_url(url):
        """ 輸出前驗證: 網址是否存在
        """
        if is_alive_url(url):
            return url
        raise ValueError(f'網址無法連線: {url}')

    @root_validator
    def fill_average_hash(cls, value_dict: dict):
        """ 輸出前自動填入 average_hash
        """
        average_hash_str = value_dict['average_hash_str']
        if average_hash_str is None:
            value_dict['average_hash_str'] = get_average_hash_str(
                value_dict['url'])
        return value_dict


class EmojiOut(EmojiBase, OutBase):
    id: UUID
    created_at: datetime.datetime
    average_hash_str: str
    tag_list: List[TagOut]

    @validator('tag_list')
    def order_tags_by_name(cls, tag_list):
        """ 輸出前驗證: 網址是否存在
        """
        return sorted(tag_list, key=lambda tag: tag.name)


class EmojiAddTagsIn(BaseModel):
    """ 更新表符的標籤列表 模型

    Args:
       tags_str (str): 標籤字串，使用逗號分隔
    """
    tags_str: str

    @property
    def tag_str_list(self) -> List[str]:
        """ 以逗號分隔的標籤字串，並去掉前後空白，且不會輸出空白字串

        Returns:
            List[str]
        """
        return tags_str_2_tag_str_list(self.tags_str)


if __name__ == '__main__':
    emojiIn = EmojiIn(
        url='https://emos.plurk.com/22aafc0710c5febfdf95cdee1aa74f1b_w48_h48.jpeg')
    print(emojiIn)
    print(type(emojiIn.average_hash_str))

    print(imagehash.hex_to_hash(emojiIn.average_hash_str))
