from pathlib import Path  # nopep8
import sys  # nopep8
sys.path.append(str(Path(__file__).resolve().parent.parent))  # nopep8
from tortoise import Tortoise, run_async
from db.models import *
import pandas as pd
import sqlite3
from tqdm import trange
from loguru import logger

myapp_emoji_df = None
taggit_tag_df = None
taggit_taggeditem_df = None
myapp_combindemoji_df = None


def prepare_dfs():
    """ 獲取 DF 資料表
    """
    global myapp_emoji_df
    global taggit_tag_df
    global taggit_taggeditem_df
    global myapp_combindemoji_df

    # 設定各個資料表獲取數量
    # IMPORT_DATA_N = -1
    IMPORT_DATA_N = 200

    # 新增表符: 先獲取 CSV 中的表符資料
    logger.info(f'載入 myapp_emoji_df ...')
    myapp_emoji_df = pd.read_csv(
        Path(__file__).parent / '../data/myapp_emoji.csv'
    ).head(IMPORT_DATA_N)

    # 新增標籤: 先獲取 CSV 中的標籤資料
    logger.info(f'載入 taggit_tag_df ...')
    taggit_tag_df = pd.read_csv(
        Path(__file__).parent / '../data/taggit_tag.csv'
    ).head(IMPORT_DATA_N)

    logger.info(f'載入 taggit_taggeditem_df ...')
    taggit_taggeditem_df = pd.read_csv(
        Path(__file__).parent / '../data/taggit_taggeditem.csv'
    ).head(IMPORT_DATA_N)

    logger.info(f'載入 myapp_combindemoji_df ...')
    myapp_combindemoji_df = pd.read_csv(
        Path(__file__).parent / '../data/myapp_combindemoji.csv'
    ).head(IMPORT_DATA_N)


async def init_db():
    """ 初始化資料庫
    """
    await Tortoise.init(db_url="sqlite://db.sqlite3", modules={"models": ["db.models"]})
    await Tortoise.generate_schemas()


async def import_emoji_data():
    """ 自 CSV 匯入表符資料
    """
    # 批量新增表符
    for emoji_i in trange(len(myapp_emoji_df)):

        # 新增表符
        emoji = await Emoji.create(
            url=myapp_emoji_df.iloc[emoji_i]["url"],
            average_hash_str=myapp_emoji_df.iloc[emoji_i]["imagehash_str"],
        )

        # 獲取表符的標籤
        emoji_int_id = myapp_emoji_df.iloc[emoji_i]['id']
        tag_id_list = taggit_taggeditem_df[
            (taggit_taggeditem_df['object_id'] == emoji_int_id) &
            (taggit_taggeditem_df['content_type_id'] == 9)
        ]['tag_id']
        tag_str_list = taggit_tag_df[taggit_tag_df['id'].isin(
            tag_id_list)]['name']
        tags_str = ','.join(
            [tag_str for tag_str in tag_str_list if isinstance(tag_str, str)])

        # 新增表符的標籤
        await emoji.add_tags(
            EmojiAddTagsIn(tags_str=tags_str)
        )

    # sql.close()


async def main():
    logger.info(f'初始化資料庫')
    await init_db()

    logger.info(f'獲取 DF 資料表')
    prepare_dfs()

    logger.info(f'自 CSV 匯入表符')
    await import_emoji_data()

    # logger.info(f'自 CSV 匯入標籤')
    # await import_tag_data()

    # await import_tagged_emoji_data()


if __name__ == '__main__':
    run_async(main())
