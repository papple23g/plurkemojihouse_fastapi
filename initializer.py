from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.starlette import register_tortoise


def init(app: FastAPI):
    """ 初始化 Fastapi 程序

    Args:
        app (FastAPI)
    """
    init_db(app)
    init_middleware(app)


def init_db(app: FastAPI):
    """ Init database models.

    Args:
        app (FastAPI)
    """
    register_tortoise(
        app,
        db_url='sqlite://db.sqlite3',
        generate_schemas=True,
        modules={"models": ["db.models"]},
    )


def init_middleware(app: FastAPI):
    """
    Initialize middleware
    設定防火牆: 解決 CORS 問題

    Args:
        app (FastAPI)
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
