from typing import Callable

import pytest
import sqlalchemy as sa
from bs4 import BeautifulSoup
from fastapi.testclient import TestClient

from textboard import db, main

# テスト用のSQLite3のメモリDBの作成
# cf. https://docs.sqlalchemy.org/en/14/core/engines.html#sqlite
engine = sa.create_engine("sqlite:///textboard-for-test", echo=True)
db.create_table(engine)


# DBをテスト用のものに差し替えます
# cf. https://fastapi.tiangolo.com/advanced/testing-dependencies/
def get_test_engine() -> sa.engine.Connectable:
    return engine


main.app.dependency_overrides[main.get_engine] = get_test_engine

# テストクライアントの作成
# cf. https://fastapi.tiangolo.com/tutorial/testing/
client = TestClient(main.app)


# pytestのfixtureを使ってテスト毎にDBの初期化をします
# cf. https://docs.pytest.org/en/stable/fixture.html
@pytest.fixture
def setup_db():  # type: ignore
    db.delete_all(engine)
    yield


# HTMLのレスポンスをテストするためにBeautiful Soupを利用しています
# cf. https://www.crummy.com/software/BeautifulSoup/
def test_empty_message(setup_db: Callable[[], None]) -> None:
    """何も投稿しない場合はメッセージを表示しない"""
    response = client.get("/")
    assert response.status_code == 200
    soup = BeautifulSoup(response.content, "html.parser")
    assert len(soup.find_all(class_="message-body")) == 0


def test_post_message(setup_db: Callable[[], None]) -> None:
    """投稿したものが表示される"""
    message = "test test"
    response = client.post("/", data={"message": message})
    assert response.status_code == 200
    soup = BeautifulSoup(response.content, "html.parser")
    message_all = soup.find_all(class_="message-body")
    assert len(message_all) == 1
    assert message_all[0].get_text() == message


def test_post_message_of_zero_length(setup_db: Callable[[], None]) -> None:
    """空のメッセージは投稿できない"""
    message = ""
    response = client.post("/", data={"message": message})
    assert response.status_code == 200
    soup = BeautifulSoup(response.content, "html.parser")
    assert len(soup.find_all(class_="message-body")) == 0
    assert soup.find(id="error").get_text() == "メッセージを入力してください"


def test_post_too_long_message(setup_db: Callable[[], None]) -> None:
    """長すぎるメッセージは投稿できない"""
    message = "test test test"
    response = client.post("/", data={"message": message})
    assert response.status_code == 200
    soup = BeautifulSoup(response.content, "html.parser")
    assert len(soup.find_all(class_="message-body")) == 0
    assert soup.find(id="error").get_text() == "メッセージが長すぎます"
