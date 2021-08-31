from dataclasses import dataclass, asdict
from browser.html import *
from browser import bind, window, alert, ajax, aio, prompt, doc
import json
from typing import List, Dict, Any, Optional, Union
import inspect

from py.utils import *
Emoji = None
EmojiQuery = None


@dataclass
class EmojiQuery:
    """ 查詢表符參數
    """
    page_n: int = 1
    page_size_n: int = 30
    tags_str: str = None

    @classmethod
    def from_url(cls, url: str) -> EmojiQuery:
        """ 以 url 取得查詢表符參數

        Args:
            url (str)

        Returns:
            EmojiQuery
        """
        url_query_dict = get_url_query_dict(url)
        tags_str = url_query_dict.get('tags_str', None)
        tags_str: Optional[str] = tags_str and str(tags_str)
        return cls(
            page_n=int(url_query_dict.get('page_n', cls.page_n)),
            page_size_n=int(url_query_dict.get(
                'page_size_n', cls.page_size_n)),
            tags_str=tags_str,
        )

    def to_url_query_str(self, page_n: int = None) -> str:
        """取得查詢表符參數的 url query string

        Args:
            page_n (int, optional): 指定頁籤編號. Defaults to None.

        Returns:
            str
        """
        url_query_dict = asdict(self)
        if page_n:
            url_query_dict['page_n'] = page_n
        return '&'.join([f'{k}={v}' for k, v in url_query_dict.items() if v])


@dataclass
class Tag:
    """ 標籤元素
    """
    name: str
    id: str = None

    @property
    def span(self) -> SPAN:
        """ 藍色圓潤標籤元素

        Returns:
            SPAN
        """
        return SPAN(
            SPAN(
                self.name,
                style=dict(
                    fontSize=14,
                    fontWeight='bold',
                    color='white'
                )
            ),
            style=dict(
                backgroundColor='rgba(50,100,256,0.7)',
                border=None,
                borderRadius="15px",
                boxShadow='2px 2px #ccc',
                textAlign='center',
                cursor='pointer',
                padding='5px 12px',
                marginTop='10px',
                marginRight='5px',
                lineHeight="2",
            )
        )


@dataclass
class ApiEmojiOut:
    """ 表符列表結果
    """
    emoji_list: List[Emoji]
    emoji_n: int


@dataclass
class Emoji:
    """ 表符元素
    """
    id: str
    url: str
    created_at: str
    average_hash_str: str
    tag_list: List[Tag]

    @classmethod
    def from_dict(cls, emoji_dict: dict):
        """ 輸入字典建立表符
        """
        return cls(**dict(
            id=emoji_dict['id'],
            url=emoji_dict['url'],
            created_at=emoji_dict['created_at'],
            average_hash_str=emoji_dict['average_hash_str'],
            tag_list=[
                Tag(**dict(id=tag_dict['id'], name=tag_dict['name']))
                for tag_dict in emoji_dict['tag_list']
            ],
        ))

    def update_emoji(self, emoji):
        """ 更新表符物件
        """

        # 更新表符標籤區塊: 清空並重新添加
        tag_spans_div = self.get_tr().select_one('div.tag_spans')
        tag_spans_div.clear()
        tag_spans_div <= emoji.tag_spans_div.children

        # 更新 tr 元素上的表符物件
        doc.select_one(f'tr[emoji-id="{self.id}"]').emoji = emoji

    def get_tr(self) -> TR:
        """ 獲取表符 TR 元素
        """
        return doc.select_one(f'tr[emoji-id="{self.id}"]')

    def get_emoji(self) -> Emoji:
        """ 獲取表符物件
        """
        return self.get_tr().emoji

    def get_tags_str(self) -> str:
        """ 獲取表符標籤字串
        """
        return ', '.join([tag.name for tag in self.get_emoji().tag_list])

    def get_input(self) -> INPUT:
        """ 獲取表符標籤輸入框 INPUT 元素
        """
        return doc.select_one(f'input[emoji-id="{self.id}"]')

    def onclick_copy_tags_str(self, ev):
        """ 複製標籤字串
        """
        tags_str = self.get_tags_str()
        copy_text_to_cliboard(tags_str)
        # alert(f"已複製標籤：「{tags_str}」")
        show_alert_message(f"已複製標籤：「{tags_str}」")

    async def onclick_add_new_tag(self, ev):
        """ 新增標籤
        """
        # 自 [標籤輸入框] 獲取欲新增的標嵌字串
        tags_str: str = self.get_input().value
        if not tags_str:
            return

        # 新增標籤請求後，獲取更新後的表符物件
        emoji = await self.get_emoji().put_tags(tags_str)

        # 更新表符物件
        self.update_emoji(emoji)

        # 清空輸入框
        self.get_input().value = ''

    @property
    def img_div(self) -> DIV:
        """ 網格區域元素: 表符圖片

        Returns:
            DIV: [description]
        """
        return DIV(
            IMG(
                src=self.url,
                style=dict(
                    position="relative",
                    display="inline-block"
                )
            ),
        )

    @property
    def iconTool_is_div(self) -> DIV:
        """ 網格區域元素: 表符操作工具: 加入收藏按鈕、檢視組表符按鈕

        Returns:
            DIV
        """
        _icon_style_dict = dict(
            color="#ccc",
            border="solid 2px #ccc",
            padding="2px",
            cursor="pointer",
            fontSize="17px",
            marginLeft="2px",
            marginBottom="2px",
            borderRadius="3px",
        )
        _word_icon_style_dict = {
            **_icon_style_dict,
            **dict(fontSize="15px"),
        }
        _send_add_new_tag_btn_style_dict = dict(
            color="cornflowerblue",
            border="2px solid cornflowerblue",
            padding="3 10",
            cursor="pointer",
            marginLeft="2px",
            marginBottom="2px",
            borderRadius="11px",
            fontSize="15px",
        )

        return DIV(
            [
                # icon 按鈕: 複製表符
                I(
                    Class="far fa-copy",
                    style=_icon_style_dict,
                ),
                # icon 按鈕: 檢視組合表符
                I(
                    Class="fas fa-th-large",
                    style=_icon_style_dict,
                ),
                # icon 按鈕: 收藏(愛心)
                I(
                    Class="fas fa-heart",
                    style=_icon_style_dict,
                ),
                # icon 按鈕: 搜尋相似表符
                SPAN("似", style=_word_icon_style_dict),
                # 輸入框: 輸入標籤字串列表 (按下 Enter 可直接新增標籤)
                INPUT(
                    style=dict(
                        border="2px solid rgb(170, 170, 170)",
                        borderRadius="20px",
                        width="35%",
                        marginLeft="5px",
                        maxWidth="200px",
                        outline="none",  # 不要顯示 foucs 的 outline
                        paddingLeft="12px",
                    ),
                    emoji_id=self.id,
                ).bind("keydown", lambda ev: hasattr(ev, 'key') and (ev.key == "Enter") and aio.run(self.onclick_add_new_tag(ev))),
                # 按鈕: 新增標籤
                SPAN(
                    "新增",
                    style=_send_add_new_tag_btn_style_dict
                ).bind("click", lambda ev: aio.run(self.onclick_add_new_tag(ev))),
                # icon 按鈕: 複製所有標籤字串
                I(
                    Class="fa fa-clone",
                    style=_icon_style_dict,
                ).bind("click", self.onclick_copy_tags_str),
            ],
            style=dict(
                float="left",
                width="100%",
            ),
        )

    @property
    def tag_spans_div(self) -> DIV:
        """ 網格區域元素: 標籤列表

        Returns:
            DIV
        """
        return DIV(
            [tag.span for tag in self.tag_list],
            style=dict(lineHeight='28px'),
            Class="tag_spans",
        )

    @property
    def main_tr(self) -> TR:
        """
        表格單一橫列元素 (表符和標籤)

        Attributes:
            emoji: Emoji

        Returns:
            TR
        """
        tr = TR(
            [
                # 表符儲存格
                TD(
                    self.img_div,
                    rowspan=2,
                    style=dict(
                        # 置中表符圖片
                        textAlign="center",
                        verticalAlign="middle",
                        # 儲存格格線
                        border="1px solid #dddddd",
                        paddingLeft="8px",
                    ),
                ),
                TD(self.tag_spans_div)
            ],
            emoji_id=self.id,
        )
        tr.emoji = self
        return tr

    @property
    def tool_tr(self) -> TR:
        """
        表格單一橫列元素 (表符操作工具)

        Attributes:
            emoji: Emoji

        Returns:
            TR
        """
        tr = TR(
            [
                #.###
                TD(
                    self.iconTool_is_div,
                    Class="w3-light-grey",
                    style=dict(
                        padding=3,
                    ),
                )
            ],
        )
        tr.emoji = self
        return tr

    @classmethod
    async def get_apiEmojiOut(
            cls,
            emojiQuery: EmojiQuery) -> ApiEmojiOut:
        """ 根據搜尋條件取得表符列表

        Args:
            emojiQuery (EmojiQuery): 搜尋參數

        Returns:
            List[Emoji]
        """

        # 建立搜尋表單字典
        emojiQuery_dict = {
            k: v for k, v in asdict(emojiQuery).items() if v is not None
        }

        res_dict = json.loads((await aio.get("/api/emoji", data=emojiQuery_dict)).data)

        return ApiEmojiOut(
            emoji_list=[
                cls.from_dict(emoji_dict)
                for emoji_dict in res_dict['emoji_list']],
            emoji_n=res_dict['emoji_n'],
        )

    async def put_tags(self, tags_str: str) -> Emoji:
        """ 更新表符標籤

        Args:
            tags_str (str): 多個標籤字串(使用逗號分隔)

        Returns:
            Emoji
        """
        emoji_dict = json.loads((await aio.ajax(
            "PUT",
            f"/api/emoji?id={self.id}",
            format="binary",
            data=json.dumps(dict(
                tags_str=tags_str)
            ))).data)
        return Emoji.from_dict(emoji_dict)


@dataclass
class EmojiTable:
    """ 表符列表表格

    Attributes:
        emoji_list (List[Emoji]): 表符列表
    """
    emoji_list: List[Emoji]

    @property
    def _tableCol_th_tr_thead(cls) -> THEAD:
        """ 表格標頭元素: 表符圖片、表符操作工具、標籤列表

        Returns:
            THEAD
        """
        return THEAD([
            TR(
                [
                    TH(
                        '表符',
                        style=dict(width=60, textAlign="center")
                    ),
                    TH(
                        '標籤',
                        style=dict(textAlign="center")
                    ),
                ],
                Class="w3-indigo",
            ),
        ])

    @property
    def table_div(self) -> DIV:
        """ 表格區域元素

        Returns:
            DIV
        """
        return DIV(
            TABLE(
                [
                    # 表格標頭
                    self._tableCol_th_tr_thead,
                ]+[
                    # 表符圖片 + 標籤列表儲存格橫列；表符操作工具儲存格橫列
                    (
                        emoji.main_tr + emoji.tool_tr
                    ) for emoji in self.emoji_list
                ],
                Class="w3-table w3-border w3-bordered",
            ),
            Class="w3-container",
        )


@dataclass
class EmojiTablePageBtnArea:
    """ 表符表格頁籤區域 """

    emojiQuery: EmojiQuery
    emoji_n: int
    # 頁籤樣式(使用 w3 Class 來設定)
    btn_class_str_list = [
        "w3-button",
        "w3-round",
        "w3-border",
        "w3-hover-blue"
    ]
    # hover或當前頁籤樣式(使用 w3 Class 來設定)
    hover_or_current_btn_class_str_list = [
        *btn_class_str_list,
        "w3-blue",
    ]
    margin_style_dict = dict(margin="10 5")

    @property
    def current_page_n(self):
        # 獲取當前頁數編號
        return self.emojiQuery.page_n

    @property
    def page_btn_n(self):
        # 計算頁籤按鈕數量
        return (self.emoji_n // self.emojiQuery.page_size_n) + (self.emoji_n % self.emojiQuery.page_size_n > 0)

    def a(self, page_n: int, is_current: bool = False, text: str = None) -> A:
        """ 一個頁籤超連結(A)元素

        Args:
            page_n (int): 頁數
            is_current (bool, optional): 是否為當前頁籤. Defaults to False.
            text (str, optional): 頁籤文字. Defaults to page_n.

        Returns:
            A
        """
        text = text if text else str(page_n)
        return A(
            text,
            href='/search?' +
            self.emojiQuery.to_url_query_str(page_n=page_n),
            Class=" ".join(
                self.hover_or_current_btn_class_str_list if is_current else self.btn_class_str_list
            ),
            style=self.margin_style_dict,
        )

    def ellipsis_span(self) -> SPAN:
        """ 省略頁籤 SPAN 元素

        Returns:
            SPAN
        """
        return SPAN(
            "...",
            style=self.margin_style_dict
        )

    def _page_number_btn_a_list(self) -> List[Union[A, SPAN]]:
        """ 頁籤數字按鈕元素列表

        Returns:
            List[Union[A, SPAN]]: 頁籤超連結(A)元素列表，可能含有省略符號 SPAN("...")
        """

        # 若按頁籤鈕數量少於 10 個, 則全部列出
        if self.page_btn_n < 10:
            return [
                self.a(
                    page_n=page_n,
                    is_current=(self.current_page_n == page_n),
                )
                for page_n in range(1, self.page_btn_n+1)
            ]

        # 若按頁籤鈕數量大於 10 個，且當前頁面很靠近首頁或末頁 (效果: 1 2 3 4 5 .... 7 8 9 10 11)
        if (1 <= self.current_page_n <= 5) or (self.page_btn_n-4 <= self.current_page_n <= self.page_btn_n):
            return [
                # 前段數字按鈕
                self.a(
                    page_n=page_n,
                    is_current=(self.current_page_n == page_n),
                )
                for page_n in range(1, 6)
            ]+[
                # 選擇性增補第 6 頁數字按鈕
                self.a(page_n=6)
            ]*(self.current_page_n == 5)+[
                # 省略符號 (...)
                self.ellipsis_span()
            ]+[
                # 選擇性增補倒數第 6 頁數字按鈕
                self.a(page_n=self.page_btn_n-5)
            ]*(self.current_page_n == self.page_btn_n-4)+[
                # 末段數字按鈕
                self.a(
                    page_n=page_n,
                    is_current=(self.current_page_n == page_n),
                )
                for page_n in range(self.page_btn_n-4, self.page_btn_n+1)
            ]

        # 若按頁籤鈕數量大於 10 個，且當前頁面不靠近首頁或末頁 (效果: 1 2 3 ... 5 6 7 ... 9 10 11)
        return [
            # 前段數字按鈕
            self.a(page_n=page_n)
            for page_n in range(1, 4)
        ]+[
            # 省略符號 (...)
            self.ellipsis_span()
        ]+[
            # 中段數字按鈕
            self.a(
                page_n=page_n,
                is_current=(self.current_page_n == page_n),
            )
            for page_n in range(self.current_page_n-1, self.current_page_n+2)
        ]+[
            # 省略符號 (...)
            self.ellipsis_span()
        ]+[
            # 末段數字按鈕
            self.a(page_n=page_n)
            for page_n in range(self.page_btn_n-2, self.page_btn_n+1)
        ]

    @property
    def div(self) -> DIV:
        """ 表符表格頁籤區域元素

        Returns:
            DIV
        """

        return DIV(
            [
                # 第一頁按鈕
                self.a(page_n=1, text="«"),
                # 首頁按鈕
                self.a(
                    page_n=(self.current_page_n-1 if self.current_page_n >= 2 else 1), text="‹"),
            ] +
            [
                # 數字按鈕
                *self._page_number_btn_a_list()
            ] +
            [
                # 下一頁按鈕
                self.a(
                    page_n=(self.current_page_n+1 if self.current_page_n != self.page_btn_n else self.current_page_n), text="›"),
                # 末頁按鈕
                self.a(page_n=self.page_btn_n, text="»"),
            ],
            Class="w3-container",
        )
