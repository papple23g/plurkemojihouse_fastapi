from __future__ import annotations
from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from pydantic import BaseModel
from typing import List
from schema import EmojiAddTagsIn


class Tag(models.Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=100)
    emoji_list = fields.ManyToManyField(
        'models.Emoji', related_name='_tag_list')

    @classmethod
    async def get_tag_list_by_str_list(cls, tag_str_list: List[str]) -> List[Tag]:
        """ 根據標籤名稱列表獲取標籤列表 (若資料庫無此標籤則會新增)

        Args:
            tag_str_list (List[str]): 標籤名稱列表.

        Returns:
            List[Tag]
        """
        tag_list = []
        for tag_str in tag_str_list:
            tag = await cls.filter(name=tag_str).first()
            if not tag:
                tag = await cls.create(name=tag_str)
            tag_list.append(tag)
        return tag_list


class Emoji(models.Model):
    id = fields.UUIDField(pk=True)
    url = fields.CharField(max_length=100)

    async def add_tags(self, emojiAddTagsIn: EmojiAddTagsIn):
        """ 新增標籤 (會自動忽略重複的標籤)
        """
        tag_list = await Tag.get_tag_list_by_str_list(emojiAddTagsIn.tag_str_list)
        await self._tag_list.add(*tag_list)


class CombindEmoji(models.Model):
    id = fields.UUIDField(pk=True)
    combind_url = fields.TextField()
    emoji_list = fields.ManyToManyField(
        'models.Emoji', related_name='combindEmoji_list')
