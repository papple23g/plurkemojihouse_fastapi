
from browser import document as doc
from browser.html import *
from browser import bind, window, alert, ajax, aio
from dataclasses import dataclass
import json

from py.schema import Emoji


@dataclass
class Emoji:
    id: int
    url: str

    @property
    def span(self):
        return SPAN(self.url+"(" + SPAN(self.id, style=dict(color="Red")) + ")")

    @classmethod
    async def all(cls):
        # print(json.loads((await aio.get("/emoji")).data))
        return [
            cls(**emoji_dict)
            for emoji_dict in json.loads((await aio.get("/emoji")).data)
        ]


async def main():
    emoji_list = await Emoji.all()

    for emoji in emoji_list:
        doc <= emoji.span + BR()


aio.run(main())
