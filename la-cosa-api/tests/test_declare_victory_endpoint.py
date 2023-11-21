from .test_setup import test_db, clear_db
from src.theThing.games import crud as game_crud
from src.theThing.games import schemas as game_schemas
from src.theThing.players import schemas as player_schemas
from src.theThing.players import crud as player_crud
from pony.orm import db_session
from fastapi.testclient import TestClient
from src.main import app
import pytest


@pytest.fixture(scope="module", autouse=True)
def setup_module():
    # create a game
    game_data = game_schemas.GameCreate(
        name="Test Game deck", min_players=4, max_players=5
    )
    created_game = game_crud.create_game(game_data)
    # create the owner player
    player_data = player_schemas.PlayerCreate(name="Player1", owner=True)
    created_player = player_crud.create_player(player_data, created_game.id)

    # create 4 players
    player_data = player_schemas.PlayerCreate(name="Player2", owner=False)
    created_player2 = player_crud.create_player(player_data, created_game.id)
    player_data = player_schemas.PlayerCreate(name="Player3", owner=False)
    created_player3 = player_crud.create_player(player_data, created_game.id)
    player_data = player_schemas.PlayerCreate(name="Player4", owner=False)
    created_player4 = player_crud.create_player(player_data, created_game.id)

    # make player 1 La Cosa
    player_crud.update_player(
        player_schemas.PlayerUpdate(role=3), created_player.id, created_game.id
    )

    # make other players human
    player_crud.update_player(
        player_schemas.PlayerUpdate(role=1), created_player2.id, created_game.id
    )
    player_crud.update_player(
        player_schemas.PlayerUpdate(role=1), created_player3.id, created_game.id
    )
    player_crud.update_player(
        player_schemas.PlayerUpdate(role=1), created_player4.id, created_game.id
    )

    # start the game
    game_crud.update_game(
        created_game.id,
        game_schemas.GameUpdate(state=0, play_direction=True, turn_owner=1),
    )
    # finish setup
    yield


def test_declare_victory_not_ingame(test_db):
    test_app = TestClient(app)

    # then declare victory
    response = test_app.put(
        "/game/declare-victory",
        json={"game_id": 1, "player_id": 1},
    )

    assert response.status_code == 422
    assert response.json() == {"detail": "La partida no está en juego"}


def test_declare_victory_not_lacosa():
    test_app = TestClient(app)

    game_crud.update_game(
        1,
        game_schemas.GameUpdate(state=1, play_direction=True, turn_owner=1),
    )

    # then declare victory
    response = test_app.put(
        "/game/declare-victory",
        json={"game_id": 1, "player_id": 2},
    )

    assert response.status_code == 422
    assert response.json() == {"detail": "El jugador no es La Cosa"}


def test_declare_victory_no_game():
    test_app = TestClient(app)

    # then declare victory
    response = test_app.put(
        "/game/declare-victory",
        json={"game_id": 2, "player_id": 1},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Game[2]"}


def test_declare_victory_no_player():
    test_app = TestClient(app)

    # then declare victory
    response = test_app.put(
        "/game/declare-victory",
        json={"game_id": 1, "player_id": 6},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Player[6]"}


def test_declare_victory_humans_win():
    test_app = TestClient(app)

    # then declare victory
    response = test_app.put(
        "/game/declare-victory",
        json={"game_id": 1, "player_id": 1},
    )

    assert response.status_code == 200
    assert response.json()["reason"] == "¡La cosa se equivocó! Ganan los humanos"
    for player in ["Player2", "Player3", "Player4"]:
        assert player in response.json()["winners"]


def test_declare_victory_infected_win():
    test_app = TestClient(app)

    game_crud.update_game(
        1,
        game_schemas.GameUpdate(state=1, play_direction=True, turn_owner=1),
    )

    # make players infected
    player_crud.update_player(player_schemas.PlayerUpdate(role=2), 2, 1)
    player_crud.update_player(player_schemas.PlayerUpdate(role=2), 3, 1)
    player_crud.update_player(
        player_schemas.PlayerUpdate(role=1, alive=False), 4, 1
    )

    # then declare victory
    response = test_app.put(
        "/game/declare-victory",
        json={"game_id": 1, "player_id": 1},
    )

    assert response.status_code == 200
    assert response.json()["reason"] == "¡No quedan humano vivos! Gana La Cosa e infectados"
    for player in ["Player1", "Player2", "Player3"]:
        assert player in response.json()["winners"]
