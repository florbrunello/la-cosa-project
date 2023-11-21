from .test_setup import test_db, clear_db
from src.theThing.games import crud as game_crud
from src.theThing.games import schemas as game_schemas
from src.theThing.players import schemas as player_schemas
from src.theThing.players import crud as player_crud
from src.theThing.turn import crud as turn_crud
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
        player_schemas.PlayerUpdate(role=1, quarantine=2),
        created_player.id,
        created_game.id,
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

    # finish setup
    yield


def test_finish_turn_quarantine(test_db):
    test_app = TestClient(app)

    res = test_app.post(
        "game/start", json={"game_id": 1, "player_name": "Player1"}
    )

    # get the game
    game = game_crud.get_game(game_id=1)
    game.turn.state = 5
    # update the game
    turn_crud.update_turn(game_id=1, new_turn=game.turn)

    turn_owner = game.turn.owner

    # then declare victory
    response = test_app.put(
        "/turn/finish",
        json={"game_id": 1},
    )

    updated_game = game_crud.get_game(game_id=1)

    assert response.json() == {
        "message": "Turno finalizado. Ahora el turno es de Player2",
    }
    assert response.status_code == 200
    for player in updated_game.players:
        if player.table_position == turn_owner:
            assert player.quarantine == 1
        else:
            assert player.quarantine == 0
