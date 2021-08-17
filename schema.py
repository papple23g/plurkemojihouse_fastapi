
from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from pydantic import BaseModel, validator
from typing import List, Optional
from uuid import UUID
import requests


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
    tags_str: str

    @validator('url')
    def format_url(url):
        """ 輸出格式化: 去除中間空白與頭尾空白
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
        res = requests.head(url)
        if res.status_code == 200:
            return url
        raise ValueError(f'網址無法連線: {url}')


class EmojiOut(EmojiBase, OutBase):
    id: UUID
    tag_list: List[TagOut]


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
        tag_str_list = [
            tag_str.replace('　', ' ').strip()
            for tag_str in self.tags_str.split(',')
        ]
        return [
            tag_str for tag_str in tag_str_list if tag_str
        ]
