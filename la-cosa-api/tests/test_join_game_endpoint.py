from fastapi.testclient import TestClient
from src.main import app
from pony.orm import db_session, rollback
from .test_setup import test_db, clear_db
from src.theThing.games import crud

client = TestClient(app)


@db_session
def test_join_game_success(test_db):
    # Test #1: join a player to a game with valid data
    # Create a game first
    game_data = {
        "game": {"name": "Test Game", "min_players": 4, "max_players": 5},
        "host": {"name": "Test Host"},
    }
    response = client.post("/game/create", json=game_data)

    # Players data for joining
    join_data = {
        "players": [
            {"game_id": 1, "player_name": "Test Player 2"},
            {"game_id": 1, "player_name": "Test Player 3"},
            {"game_id": 1, "player_name": "Test Player 4"},
        ]
    }

    # Join players to the game
    playerid = 2
    for player in join_data["players"]:
        response = client.post("/game/join", json=player)
        assert response.status_code == 200
        assert response.json() == {
            "message": "El jugador se unió con éxito",
            "player_id": playerid,
            "game_id": 1,
        }
        playerid += 1

    # rollback()


@db_session
def test_join_player_with_empty_name(test_db):
    # Test #2: join a player to a game with empty name
    # Players data for joining
    join_data = {"game_id": 1, "player_name": ""}

    # Join player to the game
    response = client.post("/game/join", json=join_data)
    assert response.status_code == 422
    assert response.json() == {
        "detail": "El nombre del jugador no puede ser vacío"
    }

    rollback()


@db_session
def test_join_player_with_existing_name(test_db):
    # Test #3: join a player to a game with an existing name
    join_data = {"game_id": 1, "player_name": "Test Player 3"}

    # Join player to the game
    response = client.post("/game/join", json=join_data)
    assert response.status_code == 422
    assert response.json() == {
        "detail": "Ya existe un jugador con el mismo nombre"
    }

    rollback()


@db_session
def test_join_full_game(test_db):
    # Test #4: join a player to a full game
    # We use the same game created in test #1 because rollback() is not working
    # Add one more player to reach max players
    join_data = {"game_id": 1, "player_name": "Test Player 5"}
    response = client.post("/game/join", json=join_data)
    assert response.status_code == 200

    # Try to add one more player
    join_data = {"game_id": 1, "player_name": "Test Player 6"}
    response = client.post("/game/join", json=join_data)
    assert response.status_code == 422
    assert response.json() == {"detail": "La partida está llena"}

    rollback()


@db_session
def test_join_started_game(test_db):
    # Test #5: join a player to a started game

    # Start the previous game
    game_data = {"game_id": 1, "player_name": "Test Host"}
    response = client.post("/game/start", json=game_data)

    # Join a player to the game
    join_data = {"game_id": 1, "player_name": "Test Player 5"}
    response = client.post("/game/join", json=join_data)
    assert response.status_code == 422
    assert response.json() == {"detail": "La partida ya ha comenzado"}

    rollback()


@db_session
def test_join_invalid_game(test_db):
    # Test #6: join a player to a non-existent game
    # Players data for joining
    join_data = {"game_id": 2, "player_name": "Test Player 1"}

    # Join player to the game
    response = client.post("/game/join", json=join_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "No se encontró la partida"}

    rollback()


@db_session
def test_join_same_name_diff_games(test_db):
    # Test #7: join a player with the same name to different games
    # Create two games
    game1_data = {
        "game": {"name": "Test Game A", "min_players": 4, "max_players": 5},
        "host": {"name": "Test Host A"},
    }
    game2_data = {
        "game": {"name": "Test Game B", "min_players": 4, "max_players": 5},
        "host": {"name": "Test Host B"},
    }
    response = client.post("/game/create", json=game1_data)
    id_game_A = response.json().get("game_id")

    response = client.post("/game/create", json=game2_data)
    id_game_B = response.json().get("game_id")

    # Join a player with the same name to both games
    join_data = {"game_id": id_game_A, "player_name": "Test Player SameName"}
    response = client.post("/game/join", json=join_data)
    assert response.status_code == 200
    assert response.json() == {
        "message": "El jugador se unió con éxito",
        "player_id": 8,
        "game_id": id_game_A,
    }

    join_data = {"game_id": id_game_B, "player_name": "Test Player SameName"}
    response = client.post("/game/join", json=join_data)
    assert response.json() == {
        "message": "El jugador se unió con éxito",
        "player_id": 9,
        "game_id": id_game_B,
    }

    rollback()
