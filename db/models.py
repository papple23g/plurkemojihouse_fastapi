from __future__ import annotations
import imagehash
import pandas as pd
from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from pydantic import BaseModel
from typing import List
from tortoise.query_utils import Prefetch

from schema import EmojiAddTagsIn


class Tag(models.Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=100)
    created_at = fields.DatetimeField(auto_now_add=True)
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
    average_hash_str = fields.CharField(max_length=100)
    created_at = fields.DatetimeField(auto_now_add=True)

    async def add_tags(self, emojiAddTagsIn: EmojiAddTagsIn):
        """ 新增標籤 (會自動忽略重複的標籤)
        """
        tag_list = await Tag.get_tag_list_by_str_list(emojiAddTagsIn.tag_str_list)
        await self._tag_list.add(*tag_list)

    async def remove_tag(self, tag_id: str):
        """ 移除標籤
        """
        tag = await Tag.filter(id=tag_id).first()
        if tag:
            await self._tag_list.remove(tag)

    @classmethod
    async def get_similar_emoji_list(
            cls,
            average_hash_str: str,
            output_n: int = 20) -> List[Emoji]:
        """ 獲取相似圖片的表符
        """
        # 獲取所有表符平均哈希值字典 → 產生 DF 資料表
        emoji_dict_list = await Emoji.all().values('id', 'average_hash_str')
        emoji_df = pd.DataFrame(emoji_dict_list)
        emoji_df['average_hash'] = emoji_df['average_hash_str'].apply(
            lambda x: imagehash.hex_to_hash(x))
        # 新增欄位: 並計算相似度差異值 (越小越相似)
        emoji_df['average_hash_diff_int'] = emoji_df['average_hash'] - \
            imagehash.hex_to_hash(average_hash_str)

        return [
            await Emoji.get(id=emoji_id).prefetch_related(
                Prefetch("_tag_list", Tag.all(), to_attr="tag_list")
            )
            for emoji_id in emoji_df.sort_values(by=['average_hash_diff_int']).head(output_n)['id']
        ]


# class CombindEmoji(models.Model):
#     id = fields.UUIDField(pk=True)
#     combind_url = fields.TextField()
#     emoji_list = fields.ManyToManyField(
#         'models.Emoji', related_name='combindEmoji_list')
# if __name__=='__main__':

    # await Emoji.get_similar_emoji_list
