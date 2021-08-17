from fastapi.params import Query
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

from initializer import init
from db.models import *
from schema import *


# 建立 app 實例
app = FastAPI()


# 設定前端文件:靜態文件與HTML檔
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/py", StaticFiles(directory="py"), name="py")
templates = Jinja2Templates(directory=".")


@app.get("/", response_class=HTMLResponse)
async def 首頁(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/emoji", response_model=List[EmojiOut])
async def 獲取表符列表():
    emoji_list = await Emoji.all().prefetch_related(
        Prefetch("_tag_list", Tag.all(), to_attr="tag_list")
    )
    return [EmojiOut.from_orm(emoji) for emoji in emoji_list]


@app.post("/emoji")
async def 新增表符列表(emojiIn: EmojiIn):
    emoji, _ = await Emoji.get_or_create(
        url=emojiIn.url,
    )
    await emoji.add_tags(EmojiAddTagsIn(tags_str=emojiIn.tags_str))
    return JSONResponse(status_code=status.HTTP_200_OK)


@app.delete("/emoji")
async def 刪除表符(id: UUID):
    emoji = await Emoji.filter(id=id).first()
    if emoji:
        await emoji.delete()
    return JSONResponse(status_code=status.HTTP_200_OK)


@app.delete("/tag")
async def 刪除標籤(id: UUID):  # .### 待測試
    tag = await Tag.filter(id=id).first()
    if tag:
        await tag.delete()
    return JSONResponse(status_code=status.HTTP_200_OK)


@app.put("/emoji")
async def 更新表符_追加標籤(
        *,
        id: UUID = Query(..., description='表符 ID'),
        emojiAddTagsIn: EmojiAddTagsIn):

    emoji = await Emoji.filter(id=id).first()
    if not emoji:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND)

    await emoji.add_tags(emojiAddTagsIn)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "更新成功"})


init(app)

if __name__ == '__main__':
    import uvicorn

    HOST: str = '127.0.0.1'
    PORT: int = 8000

    logger.info(f'首頁 請照訪：http://{HOST}:{PORT}')
    logger.info(f'API Docs 請照訪：http://{HOST}:{PORT}/docs')

    uvicorn.run(
        f'{str(Path(__file__).stem)}:app',
        host=HOST,
        port=PORT,
        reload=True,
        debug=True,
    )
