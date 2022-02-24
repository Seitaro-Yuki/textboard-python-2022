from typing import Optional

import sqlalchemy as sa
from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from textboard import db
from textboard.config import Settings
from textboard.models import Message

app = FastAPI()

# FastAPIの静的ファイル配信の設定
# cf. https://fastapi.tiangolo.com/tutorial/static-files/
app.mount("/static", StaticFiles(directory="static"), name="static")

# FastAPIでJinja2というテンプレートエンジンを使うための設定
# cf. https://fastapi.tiangolo.com/advanced/templates/
templates = Jinja2Templates(directory="templates")

# SQLAlchemyの初期設定
# cf. https://docs.sqlalchemy.org/en/14/core/engines.html
settings = Settings()
db_engine = sa.create_engine(settings.database_url, echo=True)
db.create_table(db_engine)


# FastAPIのDI用のメソッド
# cf. https://fastapi.tiangolo.com/tutorial/dependencies/
def get_engine() -> sa.engine.Connectable:
    return db_engine


# GET / と POST / の両方で使うレスポンス作成
def make_response(
    request: Request, engine: sa.engine.Connectable, error: Optional[str]
) -> Response:
    messages = db.find_all(engine)
    context = {"request": request, "messages": messages, "error": error}
    return templates.TemplateResponse("index.html", context)


# FastAPIでHTMLを返すにはresponse_classを指定する必要があります
# cf. https://fastapi.tiangolo.com/advanced/custom-response/
@app.get("/", response_class=HTMLResponse)
async def get(
    request: Request, engine: sa.engine.Connectable = Depends(get_engine)
) -> Response:
    return make_response(request, engine, None)


# FastAPIでformのデータを受け取るためにはパラメータにFormを使う必要があります
# cf. https://fastapi.tiangolo.com/tutorial/request-forms/
@app.post("/", response_class=HTMLResponse)
async def post(
    request: Request,
    engine: sa.engine.Connectable = Depends(get_engine),
    message: Optional[str] = Form(None),
) -> Response:
    error = None
    if message is None or len(message) <= 0:
        error = "メッセージを入力してください"
    elif len(message) > settings.max_message_length:
        error = "メッセージが長すぎます"
    else:
        db.add(engine, Message(body=message))
    return make_response(request, engine, error)
