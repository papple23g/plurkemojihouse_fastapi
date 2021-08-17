from tortoise import Tortoise, run_async
from db.models import *


async def init_db():
    await Tortoise.init(db_url="sqlite://db.sqlite3", modules={"models": ["db.models"]})
    await Tortoise.generate_schemas()


async def main():
    await init_db()

    emoji_list = await Emoji.all().order_by('-created_at').offset(100).limit(3)
    for emoji in emoji_list:
        print(emoji.id)

if __name__ == '__main__':
    run_async(main())
