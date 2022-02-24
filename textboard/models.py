from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Message(BaseModel):
    """掲示板に投稿されたメッセージ"""

    # モデルの実装にはFastAPIで採用されているPydanticを利用
    # cf. https://pydantic-docs.helpmanual.io/usage/models/

    id: Optional[int]
    body: str
    created_at: datetime = datetime.now()
