from tortoise import Tortoise, run_async
from db.models import *
from tortoise.query_utils import Q
from functools import reduce


async def init_db():
    await Tortoise.init(db_url="sqlite://db.sqlite3", modules={"models": ["db.models"]})
    await Tortoise.generate_schemas()


async def main():
    await init_db()

    tag_str_list = ["Ib", "臉紅"]
    emoji_list = await Emoji.filter(
        reduce(
            lambda x, y: x and y,
            [Q(_tag_list__name__in=[tag_str]) for tag_str in tag_str_list]
        )
    ).order_by('-created_at').distinct()
    for emoji in emoji_list:
        print(emoji.id)

if __name__ == '__main__':
    run_async(main())
