from fastapi.testclient import TestClient
from src.main import app
from pony.orm import db_session, rollback
from tests.test_setup import test_db


client = TestClient(app)


@db_session
def test_get_game_success(test_db):
    # Test getting a game that exists
    # Create a game first
    game_data = {
        "game": {"name": "Test Game", "min_players": 4, "max_players": 6},
        "host": {"name": "Test Host"},
    }
    client.post("/game/create", json=game_data)

    # Get the game
    response = client.get("/game/1")
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "name": "Test Game",
        "min_players": 4,
        "max_players": 6,
        "state": 0,
        "play_direction": True,
        "turn": None,
        "players": [
            {
                "name": "Test Host",
                "table_position": 1,
                "alive": True,
                "quarantine": False,
            }
        ],
        "obstacles": [],
    }
    rollback()


@db_session
def test_get_nonexistent_game(test_db):
    # Test getting a game that doesn't exist
    response = client.get("/game/100")
    assert response.status_code == 404
    assert "Game[100]" in response.text
    rollback()
