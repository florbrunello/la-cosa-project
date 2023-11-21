from fastapi.testclient import TestClient
from src.main import app
from pony.orm import db_session, rollback
from tests.test_setup import test_db, clear_db


client = TestClient(app)


@db_session
def test_get_empty_game_list(test_db):
    # Test get an empty game list
    response = client.get("/game/list")
    assert response.status_code == 200
    assert response.json() == []


@db_session
def test_get_game_list(test_db):
    # Test get a game list
    # start by creating a game
    game_data = {
        "game": {
            "name": "Test Game",
            "min_players": 4,
            "max_players": 5,
        },
        "host": {"name": "Player1", "owner": True},
    }
    response = client.post("/game/create", json=game_data)
    assert response.status_code == 201

    # get the game list
    response = client.get("/game/list")
    assert response.status_code == 200
    assert response.json() == [
        {
            "name": "Test Game",
            "min_players": 4,
            "max_players": 5,
            "id": 1,
            "amount_of_players": 1,
        }
    ]
    rollback()
