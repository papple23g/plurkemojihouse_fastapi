from tortoise import Tortoise, run_async
from db.models import *
from tortoise.query_utils import Q
from functools import reduce
import imagehash
import pandas as pd
from tortoise.query_utils import Prefetch


async def init_db():
    await Tortoise.init(db_url="sqlite://db.sqlite3", modules={"models": ["db.models"]})
    await Tortoise.generate_schemas()


async def main():
    await init_db()

    tag_list = [await Tag.filter(name=tag_str).first() for tag_str in ["開心", "顏文字", "好"]]
    print(tag_list)
    if not all(tag_list):
        return

    emoji_list_list = [
        await Emoji.filter(_tag_list__in=[tag])
        for tag in tag_list
    ]

    emoji_id_set = reduce(lambda x, y: x & y, [
        set(emoji.id for emoji in emoji_list) for emoji_list in emoji_list_list])

    emoji_query = Emoji.filter(id__in=emoji_id_set)

    emoji_list = await emoji_query.prefetch_related(
        Prefetch("_tag_list", Tag.all(), to_attr="tag_list")
    )
    print('emoji_list', emoji_list)
    for emoji in emoji_list:
        print(emoji.url)
        print([tag.name for tag in emoji.tag_list])

if __name__ == '__main__':
    run_async(main())
