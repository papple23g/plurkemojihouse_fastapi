from dataclasses import dataclass
from browser.html import *
from browser import document, html, aio
import json
from typing import List, Dict, Any, Union


@dataclass
class Tag:
    id: int
    name: str


@dataclass
class Emoji:
    id: int
    url: str
    tag_list: List[Tag]

    @property
    def span(self):
        return SPAN(self.url+"(" + SPAN(self.id, style=dict(color="Red")) + ")")

    @classmethod
    async def all(cls):
        return [
            cls(**emoji_dict)
            for emoji_dict in json.loads((await aio.get("/emoji")).data)
        ]
