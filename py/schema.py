from string import ascii_letters
import random as ran
from dataclasses import dataclass, asdict
from browser.html import *
from browser import bind, window, alert, ajax, aio, prompt, doc
import json
from typing import List, Dict, Any, Optional, Union, Tuple

from py.utils import *
Emoji = None
EmojiQuery = None


@dataclass
class EmojiQuery:
    """ 查詢表符參數

    Args:
        page_n(int): 當前頁數 Defaults to 1
        page_size_n(int): 每頁顯示結果數量. Defaults to 30
        tags_str(str): 輸入框或表格標籤的搜尋標籤文字. Defaults to None
        tag_str(str): 在標籤搜尋結果被點擊的標籤名稱，若有值則搜索標籤將以此為主. Defaults to None
        similar_emoji_id(str): 搜尋相似表符的表符 ID. Defaults to None
    """
    page_n: int = 1
    page_size_n: int = 30
    tags_str: str = None
    tag_str: str = None
    similar_emoji_id: str = None

    @classmethod
    def from_url(cls, url: str = window.location.href) -> EmojiQuery:
        """ 以 url 取得查詢表符參數

        Args:
            url (str): 分析自查詢表符參數的 url. Defaults to window.location.href

        Returns:
            EmojiQuery
        """
        url_query_dict = get_url_query_dict(url)

        tags_str = url_query_dict.get('tags_str', None)
        tags_str: Optional[str] = tags_str and str(tags_str)

        tag_str = url_query_dict.get('tag_str', None)
        tag_str: Optional[str] = tag_str and str(tag_str)

        similar_emoji_id = url_query_dict.get('similar_emoji_id', None)
        similar_emoji_id: Optional[str] = similar_emoji_id and str(
            similar_emoji_id)

        return cls(
            page_n=int(url_query_dict.get('page_n', cls.page_n)),
            page_size_n=int(url_query_dict.get(
                'page_size_n', cls.page_size_n)),
            tags_str=tags_str,
            tag_str=tag_str,
            similar_emoji_id=similar_emoji_id,
        )

    def _to_url_query_str(self, **update_kw_dict) -> str:
        """ 取得查詢表符參數的 url query string

        **update_kw_dict : 欲更新的參數字典

        Returns:
            str
        """
        url_query_dict = {**asdict(self), **update_kw_dict}
        return '&'.join([f'{k}={v}' for k, v in url_query_dict.items() if v])

    def to_url(self, **update_kw_dict) -> str:
        """ 取得查詢表符參數的 url

        **update_kw_dict : 欲更新的參數字典

        Returns:
            str
        """
        return '/search?' + self._to_url_query_str(**update_kw_dict)


@dataclass
class Tag:
    """ 標籤元素
    """
    name: str
    id: str = None

    async def onrightclick_delete(self, ev):
        """ 右鍵刪除標籤
        """
        # 防止跳出右鍵清單
        ev.preventDefault()
        # 跳出視窗確認是否要刪除標籤
        if not window.confirm(
                f"確定要刪除 [{self.name}] 這個標籤嗎?"):
            return

        # 移除標籤 SPAN 元素
        ev.currentTarget.remove()

        # 送出請求: 刪除標籤
        await aio.ajax(
            "DELETE",
            f"/api/tag?id={self.id}",
        )

    @property
    def _span(self) -> SPAN:
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
            tag_id=self.id,
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
                # 隨著寬度自動換行
                lineBreak='anywhere',
            )
        )

    @property
    def span(self) -> SPAN:
        """ 表符表格中的標籤元素

        Returns:
            SPAN
        """
        return SPAN(
            A(
                self._span,
                href=EmojiQuery(tags_str=self.name).to_url(),
                # 隱藏超連結底線
                style=(dict(textDecoration='none',)),
            )
        ).bind(
            # 綁定事件: 右鍵刪除標籤
            'contextmenu', lambda ev: aio.run(self.onrightclick_delete(ev))
        )

    @property
    def search_result_span(self) -> SPAN:
        """ 標籤搜尋結果中的標籤元素

        Returns:
            SPAN
        """

        # 分析網址查詢參數字典
        emojiQuery = EmojiQuery.from_url()

        return SPAN(
            A(
                self._span,
                href=emojiQuery.to_url(tag_str=self.name),
                # 隱藏超連結底線
                style=(dict(textDecoration='none',)),
            )
        )


@dataclass
class Emoji:
    """ 表符元素
    """
    id: str
    url: str
    created_at: str
    average_hash_str: str
    tag_list: List[Tag]

    @property
    def for_copy_url(self) -> str:
        """ 複製用的表符網址
        """
        return f'*{self.url}*'

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

    def onclick_copy_emoji_url(self, ev):
        """ 複製表符網址
        """
        copy_text_to_cliboard(self.for_copy_url)
        show_alert_message(f"已複製表符")

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
                    display="inline-block",
                    cursor="pointer",
                )
            ),
        ).bind("click", self.onclick_copy_emoji_url)

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
                ).bind("click", self.onclick_copy_emoji_url),
                # icon 按鈕: 收藏(愛心) ##
                I(
                    Class="fas fa-heart",
                    style=_icon_style_dict,
                ),
                # icon 按鈕: 檢視組合表符 ##
                I(
                    Class="fas fa-th-large",
                    style=_icon_style_dict,
                ),
                # icon 按鈕: 搜尋相似表符
                A(
                    SPAN("似", style=_word_icon_style_dict),
                    href=f"/search?similar_emoji_id={self.id}",
                    # 隱藏超連結底線
                    style=dict(textDecoration='none'),
                ),
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
    async def get_emoji_list_and_emoji_n_tuple(
            cls,
            emojiQuery: EmojiQuery) -> Tuple[List[Emoji], int]:
        """ 根據搜尋條件取得表符列表

        Args:
            emojiQuery (EmojiQuery): 搜尋參數

        Returns:
            Tuple[List[Emoji], int]
        """

        # 建立搜尋表單字典
        emojiQuery_dict = {
            k: v for k, v in asdict(emojiQuery).items() if v is not None
        }

        # 取得表符列表(自 res.body 中取得) 以及 表符總數(自 res.headers 中取得)
        get_emojis_res = (await aio.get("/api/emoji", data=emojiQuery_dict))
        emoji_n = int(get_emojis_res.response_headers.get("emoji_n", 0))
        emoji_dict_list = json.loads(get_emojis_res.data)

        return [
            cls.from_dict(emoji_dict)
            for emoji_dict in emoji_dict_list
        ], emoji_n

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
            data=json.dumps(dict(tags_str=tags_str)))).data)
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
            href=self.emojiQuery.to_url(page_n=page_n),
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


@dataclass
class EmojiSearchForm:
    """ 表符搜尋表單

    Attributes:
        emojiQuery(EmojiQuery):  輸入參數填入表單資料網頁元素, 通常來自於網址的參數

    """
    emojiQuery: EmojiQuery

    def onclick_send_query(self, ev) -> EmojiQuery:
        """ 自表單 DIV 元素取得查詢表符參數
        """
        window.location.href = EmojiQuery(
            tags_str=doc['search_tags_str_input'].value,
        ).to_url()

    @property
    def div(self) -> DIV:
        """ 表符搜尋表單 DIV 元素

        Returns:
            DIV
        """
        return DIV(
            [
                # 第一行搜尋元素:輸入框與送出按鈕
                DIV(
                    [
                        # 搜尋標籤輸入文字框
                        INPUT(
                            value=(self.emojiQuery.tags_str or ""),
                            type="search",
                            placeholder="輸入角色/作品名/動詞/形容詞...",
                            id="search_tags_str_input",
                            style=dict(
                                border='1px solid rgb(204, 204, 204)',
                                borderRadius='15px',
                                outline='none',
                                height='35px',
                                padding='10px',
                                marginRight='7px',
                                width='250px',
                            ),
                        ).bind(
                            # 綁定事件: 按下 Enter 時觸發按下 [搜尋] 按鈕送出查詢
                            "keydown",
                            lambda ev:
                                hasattr(ev, 'key')
                                and (ev.key == "Enter")
                                and doc['search_tags_str_button'].click()
                        ),
                        # 送出搜尋按鈕
                        BUTTON(
                            "搜尋",
                            id="search_tags_str_button",
                            style=dict(
                                fontFamily="微軟正黑體",
                                marginBottom="7px",
                            ),
                        ).bind("click", self.onclick_send_query),
                    ],
                ),
                # 第二行搜尋元素: 進階搜尋設定區域
                DIV(
                    [
                        # 勾選元素: 顯示我的收藏
                        DIV(
                            [
                                INPUT(type="checkbox"),
                                SPAN(
                                    " 顯示我的收藏",
                                    Class='noselect',
                                    style=dict(
                                        fontWeight="bold",
                                    ),
                                ).bind("click", lambda ev:ev.currentTarget.parent.select_one('input').click()),
                            ],
                            style=dict(
                                cursor="pointer",
                                float="left",
                                marginRight="15px",
                            ),
                        ),

                        # 勾選元素: 組合表符
                        DIV(
                            [
                                INPUT(type="checkbox"),
                                SPAN(
                                    " 組合表符",
                                    Class='noselect',
                                    style=dict(
                                        fontWeight="bold",
                                    )
                                ).bind("click", lambda ev:ev.currentTarget.parent.select_one('input').click()),
                            ],
                            style=dict(
                                cursor="pointer",
                                float="left",
                                marginRight="15px",
                            )
                        ),

                        # 勾選元素: 組合表符
                        DIV(
                            [
                                SPAN(
                                    " 檢視模式: ",
                                    Class='noselect',
                                    style=dict(
                                        fontWeight="bold",
                                    )
                                ),
                                INPUT(
                                    type="radio",
                                    name="view_mode",
                                    value="list",
                                    checked=True,
                                )+SPAN(" 列表", Class="noselect"),
                                INPUT(
                                    type="radio",
                                    name="view_mode",
                                    value="grid",
                                    marginLeft="10px",
                                )+SPAN(" 網格", Class="noselect"),
                            ],
                            style=dict(cursor="pointer")
                        )

                    ],
                    style=dict(marginTop="15px")
                )
            ],
            style=dict(
                border="1px solid rgb(204, 204, 204)",
                borderRadius="10px",
                margin="5px 20px",
                boxShadow="grey 1px 1px 3px",
                padding="20px 20px",
                width="-webkit-fill-available",
            )
        )


async def tag_search_result_div(emojiQuery: EmojiQuery) -> DIV:
    """ 標籤搜尋結果 DIV 元素

    Args:
        emojiQuery (EmojiQuery)

    Returns:
        DIV
    """

    if not emojiQuery.tags_str:
        return DIV()

    tag_dict_list = json.loads((await aio.get(
        f"/api/tag",
        data=dict(tags_str=emojiQuery.tags_str)
    )).data)
    # tag_dict_list = tag_res_dict['tag_list']

    return DIV(
        [
            Tag(**tag_dict).search_result_span
            for tag_dict in tag_dict_list
        ],
        Class="w3-container",
        style=dict(margin="17px"),
    )
