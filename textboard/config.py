from pydantic import BaseSettings


class Settings(BaseSettings):
    """DBの設定や投稿できるメッセージの最大長などの設定"""

    # 設定オブジェクトにもPydanticを利用しているが、特に機能は活用していない
    # 設定ファイルからの読み込みなども可能
    # cf. https://pydantic-docs.helpmanual.io/usage/settings/

    database_url: str = "sqlite:///textboard.db"
    max_message_length: int = 10
