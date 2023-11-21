from .test_setup import test_db, clear_db
from src.main import app
from fastapi.testclient import TestClient
from src.theThing.players.crud import get_player
from datetime import datetime
from src.theThing.games.crud import create_game, save_log, get_logs
from src.theThing.games.schemas import GameCreate

client = TestClient(app)


def test_logs_crud(test_db):
    game = create_game(
        GameCreate(name="Test Game", min_players=4, max_players=6)
    )
    save_log(game_id=game.id, log="Test log")
    save_log(game_id=game.id, log="Test log 2")
    logs = get_logs(game_id=game.id)

    assert logs == [
        {
            "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "log": "Test log",
        },
        {
            "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "log": "Test log 2",
        },
    ]


def test_get_logs_endpoint(test_db):
    # create a game, add 3 players and start the game
    game_data = {
        "game": {"name": "Test Game2", "min_players": 4, "max_players": 6},
        "host": {"name": "Test Host"},
    }
    response = client.post("/game/create", json=game_data)
    player1_id = response.json()["player_id"]
    game_id = response.json()["game_id"]
    player2_id = client.post(
        "/game/join", json={"player_name": "Test Player 1", "game_id": game_id}
    ).json()["player_id"]
    player3_id = client.post(
        "/game/join", json={"player_name": "Test Player 2", "game_id": game_id}
    ).json()["player_id"]
    player4_id = client.post(
        "/game/join", json={"player_name": "Test Player 3", "game_id": game_id}
    ).json()["player_id"]

    # start the game
    client.post(
        "/game/start", json={"game_id": game_id, "player_name": "Test Host"}
    )
    client.put(
        "/game/steal", json={"player_id": player1_id, "game_id": game_id}
    )

    response = client.get(f"game/{game_id}/get-logs")
    assert response.status_code == 200
    assert len(response.json()) == 1
