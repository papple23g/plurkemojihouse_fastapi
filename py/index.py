
from browser import document as doc
from browser.html import *
from browser import bind, window, alert, ajax, aio

from py.schema import *
from py.utils import *


async def main():

    # 分析網址查詢參數字典
    emojiQuery = EmojiQuery.from_url()
    # print(emojiQuery)

    # 查詢表符表單區域
    doc <= EmojiSearchForm(emojiQuery=emojiQuery).div

    # 標籤查詢結果區域
    doc <= (await tag_search_result_div(emojiQuery=emojiQuery))

    # 獲取表符物件列表與結果數量
    emoji_list, emoji_n = await Emoji.get_emoji_list_and_emoji_n_tuple(
        emojiQuery=emojiQuery
    )

    # 生成表符列表表格
    emojiTable = EmojiTable(
        emoji_list=emoji_list
    )

    doc <= emojiTable.table_div

    # 生成頁籤
    emojiTablePageBtnArea = EmojiTablePageBtnArea(
        emojiQuery=emojiQuery,
        emoji_n=emoji_n,
    )

    doc <= emojiTablePageBtnArea.div

aio.run(main())
