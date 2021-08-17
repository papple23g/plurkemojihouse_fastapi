from tortoise import Tortoise, run_async
from db.models import *
from tortoise.query_utils import Q
from functools import reduce
import imagehash
import pandas as pd


async def init_db():
    await Tortoise.init(db_url="sqlite://db.sqlite3", modules={"models": ["db.models"]})
    await Tortoise.generate_schemas()


async def main():
    await init_db()

    emoji_list = await Emoji.get_similar_emoji_list(average_hash_str='ef87831b81019bfb')
    for emoji in emoji_list:
        print(emoji.url)

if __name__ == '__main__':
    run_async(main())
