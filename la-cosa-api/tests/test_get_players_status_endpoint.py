from fastapi.testclient import TestClient
from src.main import app
from pony.orm import db_session, rollback
from tests.test_setup import test_db, clear_db


client = TestClient(app)


@db_session
def test_get_player_successful(test_db):
    # Test getting a player from a game that hasn't started
    # Create a game first
    game_data = {
        "game": {"name": "Test Game", "min_players": 4, "max_players": 6},
        "host": {"name": "Test Host"},
    }
    client.post("/game/create", json=game_data)

    # Get the player
    response = client.get("/game/1/player/1")
    assert response.status_code == 200
    assert response.json() == {
        "name": "Test Host",
        "owner": True,
        "id": 1,
        "table_position": 1,
        "role": None,
        "alive": True,
        "quarantine": 0,
        "card_to_exchange": None,
        "hand": [],
    }
    rollback()


@db_session
def test_get_player_successful_started(test_db):
    # Test getting a player from a game that has started
    # Create a game first
    game_data = {
        "game": {"name": "Test Game", "min_players": 4, "max_players": 6},
        "host": {"name": "Test Host"},
    }
    client.post("/game/create", json=game_data)

    # Add a few players
    client.post(
        "/game/join", json={"game_id": 1, "player_name": "Test Player 1"}
    )
    client.post(
        "/game/join", json={"game_id": 1, "player_name": "Test Player 2"}
    )
    client.post(
        "/game/join", json={"game_id": 1, "player_name": "Test Player 3"}
    )
    client.post(
        "/game/join", json={"game_id": 1, "player_name": "Test Player 4"}
    )
    # Start the game
    client.post("/game/start", json={"game_id": 1, "player_name": "Test Host"})

    # Get the player
    response = client.get("/game/1/player/1")
    assert response.status_code == 200


@db_session
def test_get_player_nonexistent(test_db):
    # Test getting a player that doesn't exist
    # Get a player that doesn't exist
    response = client.get("/game/1/player/100")
    assert response.status_code == 404
    assert "Player[100]" in response.text
    rollback()
