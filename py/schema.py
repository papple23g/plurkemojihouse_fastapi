from dataclasses import dataclass, asdict
from browser.html import *
from browser import bind, window, alert, ajax, aio, prompt
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
@dataclass
class Tag:
    """ 標籤元素
    """
    name: str
    id: str = None

    async def popup_add_tags_input_box(self, ev):
        """
        1. 在標籤元素上顯示新增標籤的輸入框
        2. 按下確定後送出請求並刷新表符的標籤列表區塊
        """

        # 獲取輸入框內的新增標籤列表字串 (ex. "tag1,tag2,tag3")
        tags_str: str = prompt('請輸入新增的標籤')
        if not tags_str:
            return

        # 獲取被點擊的標籤 SPAN 元素
        clicked_span_elt = ev.currentTarget

        # 自 TR 元素獲取表符物件
        emoji: Emoji = clicked_span_elt.closest('tr').emoji
        # 送出新增標籤請求後，獲取更新後的表符物件
        emoji = await emoji.put_tags(tags_str)

        # 更新表符標籤區塊: 清空並重新添加
        tag_spans_div = clicked_span_elt.closest('div.tag_spans')
        tag_spans_div.clear()
        tag_spans_div <= emoji.tag_spans_div.children

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
            )
        ).bind('click', lambda ev: aio.run(self.popup_add_tags_input_box(ev)))


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
        return DIV([
            I(
                Class="fas fa-heart",
                style=_icon_style_dict,
            ),
            I(
                Class="fas fa-th-large",
                style=_icon_style_dict,
            ),
        ])

    @property
    def tag_spans_div(self) -> DIV:
        """ 網格區域元素: 標籤列表

        Returns:
            DIV
        """
        add_tag_btn = SPAN(
            Tag(name="+").span,
        )

        return DIV(
            [tag.span for tag in self.tag_list] +
            [add_tag_btn],
            style=dict(lineHeight='28px'),
            Class="tag_spans",
        )

    @property
    def tr(self) -> TR:
        """
        表格單一橫列元素

        Attributes:
            emoji: Emoji

        Returns:
            TR
        """
        tr = TR(
            [
                TD(self.img_div),
                TD(self.iconTool_is_div),
                TD(self.tag_spans_div)
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
        """ 表格標題元素: 表符圖片、表符操作工具、標籤列表

        Returns:
            THEAD
        """
        return THEAD([
            TR([
                TH(
                    '表符',
                    style=dict(width=60, textAlign="center")
                ),
                TH(
                    '',
                    style=dict(width="0%")
                ),
                TH(
                    '標籤',
                    style=dict(textAlign="center")
                ),
            ]),
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
                    # 表格標頭
                    emoji.tr for emoji in self.emoji_list
                ],
                Class="w3-table-all"
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
        return self.emoji_n // self.emojiQuery.page_size_n

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
