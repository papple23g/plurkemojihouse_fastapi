from pathlib import Path  # nopep8
import sys  # nopep8
sys.path.append(str(Path(__file__).resolve().parent.parent))  # nopep8
from tortoise import Tortoise, run_async
from db.models import *
import pandas as pd
import sqlite3
from tqdm import trange

IMPORT_DATA_N = 10


async def init_db():
    await Tortoise.init(db_url="sqlite://db.sqlite3", modules={"models": ["db.models"]})
    await Tortoise.generate_schemas()


async def import_emoji_data():
    has_emoji_id_list = await Emoji.all().values_list('id', flat=True)

    # 新增表符: 先獲取 CSV 中的表符資料
    emoji_df = pd.read_csv(
        Path(__file__).parent / '../data/myapp_emoji.csv'
    ).head(IMPORT_DATA_N)
    # 批量新增表符
    await Emoji.bulk_create([
        Emoji(
            id=emoji_df.iloc[i]["id"],
            url=emoji_df.iloc[i]["url"],
        )
        for i in range(len(emoji_df))
        if int(emoji_df.iloc[i]["id"]) not in has_emoji_id_list
    ])


async def import_tag_data():
    has_tag_id_list = await Tag.all().values_list('id', flat=True)

    # 新增標籤: 先獲取 CSV 中的標籤資料
    tag_df = pd.read_csv(
        Path(__file__).parent / '../data/taggit_tag.csv'
    ).head(IMPORT_DATA_N)
    # 批量新增標籤
    await Tag.bulk_create([
        Tag(
            id=tag_df.iloc[i]["id"],
            name=tag_df.iloc[i]["name"],
        )
        for i in range(len(tag_df))
        if int(tag_df.iloc[i]["id"]) not in has_tag_id_list
    ])


async def import_tagged_emoji_data():
    taggit_tag_df = pd.read_csv(
        Path(__file__).parent / '../data/taggit_taggeditem.csv'
    ).head(IMPORT_DATA_N)

    sql = sqlite3.connect(Path(__file__).parent / '../db.sqlite3')

    tag_id_and_emoji_id_tuple_list = []
    for row_i in trange(len(taggit_tag_df)):
        tag_id_and_emoji_id_tuple_list.append(
            (
                int(taggit_tag_df.iloc[row_i]['tag_id']),
                int(taggit_tag_df.iloc[row_i]['object_id']),
            )
        )
    sql.executemany(
        'INSERT INTO "main"."tag_emoji" ("tag_id", "emoji_id") VALUES(?,?);',
        tag_id_and_emoji_id_tuple_list
    )
    sql.commit()
    sql.close()


async def main():
    await init_db()

    await import_emoji_data()
    await import_tag_data()
    await import_tagged_emoji_data()

if __name__ == '__main__':
    run_async(main())
