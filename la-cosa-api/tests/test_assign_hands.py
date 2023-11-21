from fastapi.testclient import TestClient
from src.main import app
from pony.orm import db_session, rollback
from tests.test_setup import test_db, clear_db
from src.theThing.games.crud import get_full_game

client = TestClient(app)


@db_session
def test_hands_are_not_empty(test_db):
    game_data = {
        "game": {"name": "Prueba", "min_players": 4, "max_players": 6},
        "host": {"name": "Test Host"},
    }
    response = client.post("/game/create", json=game_data)

    game_id = response.json().get("game_id")

    # join a few players
    client.post("/game/join", json={"game_id": game_id, "player_name": "P1"})
    client.post("/game/join", json={"game_id": game_id, "player_name": "P2"})
    client.post("/game/join", json={"game_id": game_id, "player_name": "P3"})

    player_name = "Test Host"
    game_data = {"game_id": game_id, "player_name": player_name}

    client.post("/game/start", json=game_data)

    full_game = get_full_game(game_id)
    hand_is_empty = False
    for player in full_game.players:
        if len(player.hand) == 0:
            hand_is_empty = True

    assert not hand_is_empty


@db_session
def test_the_thing_is_assigned(test_db):
    game_data = {
        "game": {"name": "Prueba2", "min_players": 4, "max_players": 6},
        "host": {"name": "Test Host"},
    }
    response = client.post("/game/create", json=game_data)

    game_id = response.json().get("game_id")

    # join a few players
    client.post("/game/join", json={"game_id": game_id, "player_name": "P1"})
    client.post("/game/join", json={"game_id": game_id, "player_name": "P2"})
    client.post("/game/join", json={"game_id": game_id, "player_name": "P3"})

    player_name = "Test Host"
    game_data = {"game_id": game_id, "player_name": player_name}

    client.post("/game/start", json=game_data)

    full_game = get_full_game(game_id)
    the_thing_assigned = False
    for player in full_game.players:
        for card in player.hand:
            if card.kind == 5:
                the_thing_assigned = True

    assert the_thing_assigned
    rollback()
