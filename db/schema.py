
from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from pydantic import BaseModel
from typing import List


class OutBase(BaseModel):
    class Config:
        orm_mode = True


class IdOut(OutBase):
    id: int


class TagBase(BaseModel):
    id: int
    name: str


class TagOut(TagBase, OutBase):
    ...


class EmojiBase(BaseModel):
    url: str


class EmojiIn(EmojiBase):
    ...


class EmojiOut(EmojiBase, OutBase):
    id: int
    tag_list: List[TagOut]


class AddTagsIn(BaseModel):
    """ 更新表符的標籤列表 模型
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
