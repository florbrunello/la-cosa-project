from .test_setup import test_db, clear_db
from src.theThing.games import crud as game_crud
from src.theThing.games import schemas as game_schemas
from src.theThing.messages import schemas as message_schemas
from src.theThing.messages import crud as message_crud
from pony.orm import db_session
from datetime import datetime
from fastapi.testclient import TestClient
from src.main import app


@db_session
def test_create_message(test_db):
    # first create a game
    game_data = game_schemas.GameCreate(
        name="Test Game", min_players=4, max_players=6
    )
    created_game = game_crud.create_game(game_data)

    # then create a message
    message_data = message_schemas.MessageCreate(
        content="Test message", sender="TestPlayer1"
    )

    created_message = message_crud.create_message(message_data, created_game.id)

    assert created_message.model_dump() == {
        "content": "Test message",
        "sender": "TestPlayer1",
        "date": datetime.now(tz=None).strftime("%Y-%m-%d %H:%M:%S"),
    }


@db_session
def test_get_chat(test_db):
    # add a game and 3 messages
    game_data = game_schemas.GameCreate(
        name="Test Game 2", min_players=4, max_players=6
    )
    created_game = game_crud.create_game(game_data)

    message_data = message_schemas.MessageCreate(
        content="Test message 1", sender="TestPlayer1"
    )
    created_message = message_crud.create_message(message_data, created_game.id)
    message_data = message_schemas.MessageCreate(
        content="Test message 2", sender="TestPlayer2"
    )
    created_message = message_crud.create_message(message_data, created_game.id)
    message_data = message_schemas.MessageCreate(
        content="Test message 3", sender="TestPlayer3"
    )
    created_message = message_crud.create_message(message_data, created_game.id)

    # get the chat
    chat = message_crud.get_chat(created_game.id)

    # check that the chat is ordered by date
    assert chat[0].content == "Test message 1"
    assert chat[1].content == "Test message 2"
    assert chat[2].content == "Test message 3"


def test_chat_endpoints(test_db):
    test_app = TestClient(app)

    # create a game
    game_data = game_schemas.GameCreate(
        name="Test Game 3", min_players=4, max_players=6
    )
    created_game = game_crud.create_game(game_data)

    response = test_app.put(
        f"/game/{created_game.id}/send-message",
        json={"content": "Test message 1", "sender": "TestPlayer1"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Mensaje enviado con exito",
        "data": {
            "content": "Test message 1",
            "sender": "TestPlayer1",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        },
    }

    test_app.put(
        f"/game/{created_game.id}/send-message",
        json={"content": "Test message 2", "sender": "TestPlayer2"},
    )

    response = test_app.get(f"/game/{created_game.id}/chat")
    assert response.status_code == 200
    assert response.json() == [
        {
            "content": "Test message 1",
            "sender": "TestPlayer1",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        },
        {
            "content": "Test message 2",
            "sender": "TestPlayer2",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        },
    ]
