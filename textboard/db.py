import sqlalchemy as sa

from textboard.models import Message

# SQLAlchemyの機能を使ってDBのテーブル定義をします
# cf. https://docs.sqlalchemy.org/en/14/core/schema.html
metadata = sa.MetaData()
messages_table = sa.Table(
    "messages",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("body", sa.String(256), nullable=False),
    sa.Column("created_at", sa.DateTime, nullable=False),
)


def create_table(engine: sa.engine.Connectable) -> None:
    """テーブル定義に従ってテーブル作成をする"""
    metadata.create_all(engine)


# SQLの実行はSQLAlchemy Core APIを使っています
# cf. https://docs.sqlalchemy.org/en/14/core/tutorial.html
def find_all(engine: sa.engine.Connectable) -> list[Message]:
    """すべてのメッセージを取得する"""
    with engine.connect() as connection:
        query = sa.sql.select(
            (messages_table.c.id, messages_table.c.body, messages_table.c.created_at)
        )
        return [Message(**m) for m in connection.execute(query)]


def add(engine: sa.engine.Connectable, message: Message) -> None:
    """メッセージを保存する"""
    with engine.connect() as connection:
        query = messages_table.insert()
        connection.execute(query, message.dict())


def delete_all(engine: sa.engine.Connectable) -> None:
    """メッセージをすべて消す（テスト用）"""
    with engine.connect() as connection:
        connection.execute(messages_table.delete())
