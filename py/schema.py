from dataclasses import dataclass, asdict
from browser.html import *
from browser import bind, window, alert, ajax, aio, prompt
import json
from typing import List, Dict, Any, Union

from py.utils import *


@dataclass
class EmojiQuery:
    page: int = 1
    page_size_n: int = 30
    tags_str: str = None


@dataclass
class Tag:
    """ 標籤元素
    """
    name: str
    id: str = None

    async def popup_add_tags_input_box(self, ev):
        tags_str: str = prompt('請輸入新增的標籤')
        if tags_str:
            clicked_span_elt = ev.currentTarget
            emoji_id: str = clicked_span_elt.closest('tr').emoji.id
            tag_spans_div = clicked_span_elt.closest('div.tag_spans')

            emoji: Emoji = clicked_span_elt.closest('tr').emoji

            # emoji.tag_list.append(Tag(name='tag_210818_165633', id='123'))
            # tag_spans_div.clear()
            # tag_spans_div <= emoji.tag_spans_div.children

            emoji = await emoji.put_tags(tags_str)
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
class Emoji:
    """ 表符元素
    """
    id: str
    url: str
    created_at: str
    average_hash_str: str
    tag_list: List[Tag]

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

    def add_tag(self, tag: Tag):
        self.tag_list.append(tag)

    @classmethod
    async def get_emoji_list(
            cls,
            emojiQuery: EmojiQuery):

        emojiQuery_dict = {
            k: v for k, v in asdict(emojiQuery).items() if v is not None
        }

        return [
            cls(**dict(
                id=emoji_dict['id'],
                url=emoji_dict['url'],
                created_at=emoji_dict['created_at'],
                average_hash_str=emoji_dict['average_hash_str'],
                tag_list=[
                    Tag(**dict(id=tag_dict['id'], name=tag_dict['name']))
                    for tag_dict in emoji_dict['tag_list']
                ],
            ))
            for emoji_dict in json.loads((await aio.get("/emoji", data=emojiQuery_dict)).data)
        ]

    async def put_tags(self, tags_str: str):
        """ 更新表符標籤
        """
        emoji_dict = json.loads((await aio.ajax(
            "PUT",
            f"/emoji?id={self.id}",
            format="binary",
            data=json.dumps(dict(
                tags_str=tags_str)
            ))).data)
        return Emoji(**dict(
            id=emoji_dict['id'],
            url=emoji_dict['url'],
            created_at=emoji_dict['created_at'],
            average_hash_str=emoji_dict['average_hash_str'],
            tag_list=[
                Tag(**dict(id=tag_dict['id'], name=tag_dict['name']))
                for tag_dict in emoji_dict['tag_list']
            ],
        ))


@dataclass
class EmojiTable:
    emoji_list: List[Emoji]

    @property
    def tableCol_th_tr_thead(cls) -> THEAD:
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
        return DIV(
            TABLE(
                [
                    self.tableCol_th_tr_thead,
                ]+[
                    emoji.tr for emoji in self.emoji_list
                ],
                Class="w3-table-all"
            ),
            Class="w3-container",
        )
