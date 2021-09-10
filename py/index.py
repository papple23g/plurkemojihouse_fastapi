
from browser import document as doc
from browser.html import *
from browser import bind, window, alert, ajax, aio

from py.schema import *
from py.utils import *


async def main():

    # 分析網址查詢參數字典
    emojiQuery = EmojiQuery.from_url(window.location.href)
    # print(emojiQuery)

    # 查詢表符表單區域 #.### 填入 emojiQuery
    doc <= emoji_search_form_div()

    # 標籤查詢結果區域
    doc <= (await tag_search_result_div(emojiQuery=emojiQuery))

    # 獲取表符物件列表與結果數量
    apiEmojiOut = await Emoji.get_apiEmojiOut(
        emojiQuery=emojiQuery
    )

    # 生成表符列表表格
    emojiTable = EmojiTable(
        emoji_list=apiEmojiOut.emoji_list
    )

    doc <= emojiTable.table_div

    # 生成頁籤
    emojiTablePageBtnArea = EmojiTablePageBtnArea(
        emojiQuery=emojiQuery,
        emoji_n=apiEmojiOut.emoji_n,
    )

    doc <= emojiTablePageBtnArea.div

aio.run(main())
