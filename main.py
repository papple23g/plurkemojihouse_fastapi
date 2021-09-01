from fastapi.params import Query
from pydantic.types import conint
import _pickle as cPickle
from dataclasses import dataclass
import pickle
from typing import List
from fastapi import FastAPI, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from tortoise.query_utils import Prefetch
from pathlib import Path
from loguru import logger
from uuid import UUID
from tortoise.query_utils import Q
from functools import reduce

from initializer import init
from db.models import *
from schema import *


# 建立 app 實例
app = FastAPI()


# 設定前端文件:靜態文件與HTML檔
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/py", StaticFiles(directory="py"), name="py")
templates = Jinja2Templates(directory=".")


@app.get("/search", response_class=HTMLResponse)
async def 表符搜尋頁面(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/emoji", response_model=ApiEmojiOut)
async def 獲取表符列表(
        *,
        page_n: conint(ge=1) = Query(1, description="頁數"),
        page_size_n: int = Query(30, description="每頁顯示數量"),
        tags_str: str = None,
        similar_emoji_id: str = None,):

    # 建立表符查詢池: 若有指定查詢的標籤，就先過濾出皆含有全部這些標籤(AND)的表符
    if tags_str:
        # 獲取標籤字串列表
        tag_str_list = tags_str_2_tag_str_list(tags_str)
        # 獲取標籤列表
        tag_list = [await Tag.filter(name=tag_str).first() for tag_str in tag_str_list]
        # 若有任何標籤不存在，則回傳空表符列表
        if not all(tag_list):
            return []
        # 獲取[各標籤的表符列表]列表
        emoji_list_list = [
            await Emoji.filter(_tag_list__in=[tag])
            for tag in tag_list
        ]
        # 獲取這些表符列表的表符 ID 聯集
        emoji_id_set = reduce(lambda x, y: x & y, [
            set(emoji.id for emoji in emoji_list) for emoji_list in emoji_list_list])
        # 獲取符合所有標籤的表符查詢池
        emoji_query = Emoji.filter(id__in=emoji_id_set)
    # 若有指定查詢的相似表符
    elif similar_emoji_id:
        # 獲取相似表符
        emoji = await Emoji.filter(id=similar_emoji_id).first()
        if emoji is None:
            return ApiEmojiOut()

        # 獲取相似表符的表符查詢池
        similar_emoji_list = await Emoji.get_similar_emoji_list(
            emoji.average_hash_str)
        return ApiEmojiOut(
            emoji_list=similar_emoji_list,
            emoji_n=len(similar_emoji_list),
        )

    # 若不指定查詢標籤，則直接查詢所有表符
    else:
        emoji_query = Emoji.all()

    # 計算查詢位移量
    offset_n: int = (page_n-1)*page_size_n

    # 獲取表符數量
    emoji_n = await emoji_query.count()

    # 獲取表符列表
    emoji_list = await emoji_query\
        .order_by('-created_at')\
        .offset(offset_n)\
        .limit(page_size_n)\
        .prefetch_related(
            Prefetch("_tag_list", Tag.all(), to_attr="tag_list")
        )
    return ApiEmojiOut(
        emoji_list=[EmojiOut.from_orm(emoji) for emoji in emoji_list],
        emoji_n=emoji_n,
    )


@app.post("/api/emoji")
async def 新增表符(emojiIn: EmojiIn):
    emoji, _ = await Emoji.get_or_create(
        url=emojiIn.url,
        defaults=dict(
            average_hash_str=emojiIn.average_hash_str,
        )
    )
    await emoji.add_tags(EmojiAddTagsIn(tags_str=emojiIn.tags_str))
    return JSONResponse(status_code=status.HTTP_200_OK)


@app.post("/api/emoji_list")
async def 批量新增表符列表(emojiIn_list: List[EmojiIn]):
    for emojiIn in emojiIn_list:
        await 新增表符(emojiIn)
    return JSONResponse(status_code=status.HTTP_200_OK)


@app.delete("/api/emoji")
async def 刪除表符(id: UUID):

    emoji = await Emoji.filter(id=id).first()
    if emoji:
        await emoji.delete()
    return JSONResponse(status_code=status.HTTP_200_OK)


@app.delete("/api/tag")
async def 刪除標籤(id: UUID):  # .### 待測試
    tag = await Tag.filter(id=id).first()
    if tag:
        await tag.delete()
    return JSONResponse(status_code=status.HTTP_200_OK)


@app.put("/api/emoji", response_model=EmojiOut)
async def 更新表符_追加標籤(
        *,
        id: UUID = Query(..., description='表符 ID'),
        emojiAddTagsIn: EmojiAddTagsIn):

    emoji = await Emoji.filter(id=id).first()
    if not emoji:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND)

    await emoji.add_tags(emojiAddTagsIn)

    emoji = await Emoji.get(id=id).prefetch_related(
        Prefetch("_tag_list", Tag.all(), to_attr="tag_list")
    )
    return EmojiOut.from_orm(emoji)


init(app)

if __name__ == '__main__':
    import uvicorn

    HOST: str = '0.0.0.0'
    # HOST: str = '127.0.0.1'
    PORT: int = 8000

    logger.info(f'首頁 請照訪：http://{HOST}:{PORT}/search')
    logger.info(f'API Docs 請照訪：http://{HOST}:{PORT}/docs')

    uvicorn.run(
        f'{str(Path(__file__).stem)}:app',
        host=HOST,
        port=PORT,
        reload=True,
        debug=True,
    )
