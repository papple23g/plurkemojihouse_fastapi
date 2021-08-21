
from browser import document as doc
from browser.html import *
from browser import bind, window, alert, ajax, aio

from py.schema import *
from py.utils import *


async def main():
    # 分析網址查詢參數字典
    emojiQuery = EmojiQuery.from_url(window.location.href)
    # print(emojiQuery)

    # 獲取表符物件列表
    emoji_list = await Emoji.get_emoji_list(
        emojiQuery=emojiQuery
    )

    # 生成表符列表表格
    emojiTable = EmojiTable(
        emoji_list=emoji_list
    )

    doc <= emojiTable.table_div

aio.run(main())
