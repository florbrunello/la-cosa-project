import pytest
from .test_setup import test_db
from src.theThing.cards import crud as card_crud
from src.theThing.cards.schemas import CardCreate, CardBase, CardUpdate
from src.theThing.games import crud as game_crud
from src.theThing.games.models import Game
from src.theThing.games import schemas as game_schemas
from src.theThing.players import crud as player_crud
from src.theThing.players import schemas as player_schemas
from pony.orm import db_session, rollback, commit
from src.main import app
from fastapi.testclient import TestClient

# create a pytest fixture that populates the database


@pytest.fixture(scope="module", autouse=True)
def setup_module():
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
    player_data = player_schemas.PlayerCreate(name="Player5", owner=False)
    created_player5 = player_crud.create_player(player_data, created_game.id)

    # create a second game with just one player
    game_data = game_schemas.GameCreate(
        name="Test Game deck 2", min_players=4, max_players=5
    )
    created_game2 = game_crud.create_game(game_data)
    player_data = player_schemas.PlayerCreate(name="Player6", owner=True)
    created_player6 = player_crud.create_player(player_data, created_game2.id)
    player_data = player_schemas.PlayerCreate(name="Player7", owner=False)
    created_player7 = player_crud.create_player(player_data, created_game2.id)


client = TestClient(app)


def test_leave_wrong_game(test_db):
    # test leave game with an existing player in a wrong game
    response = client.put(
        "/game/2/player/1/leave"
    )  # The player with id 1 and game 2, does not exist.
    assert response.status_code == 404
    assert response.json() == {"detail": "Player[1]"}


def test_leave_game_started(test_db):
    game = game_crud.get_full_game(2)
    players = [player for player in game.players if player.owner is False]
    game_crud.update_game(
        2, game_schemas.GameUpdate(state=1)
    )  # start the game 2, the  try to leave it
    response = client.put(f"/game/2/player/{players[0].id}/leave")
    assert response.status_code == 422
    assert response.json() == {"detail": "La partida ya ha comenzado"}
    # check that the player is still in the game
    game = game_crud.get_full_game(2)
    players_after = [player for player in game.players if player.owner is False]
    assert len(players_after) == len(players)
    assert players[0] in players_after


def test_leave_game_successful(test_db):
    game = game_crud.get_full_game(1)
    players = [player for player in game.players if player.owner is False]
    response = client.put(f"/game/1/player/{players[0].id}/leave")
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Jugador {players[0].id} abandonó la partida {game.id} con éxito"
    }
    # check that the player is not in the game anymore
    game = game_crud.get_full_game(1)
    players_after = [player for player in game.players if player.owner is False]
    assert len(players_after) == len(players) - 1
    assert players[0] not in players_after


def test_host_leaves_game(test_db):
    game = game_crud.get_full_game(1)
    players = [player for player in game.players if player.owner is False]
    response = client.put(f"/game/1/player/{players[0].id}/leave")
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Jugador {players[0].id} abandonó la partida {game.id} con éxito"
    }
    # check that the player is not in the game anymore
    game = game_crud.get_full_game(1)
    players_after = [player for player in game.players if player.owner is False]
    assert len(players_after) == len(players) - 1
    assert players[0] not in players_after
    host = [player for player in game.players if player.owner is True][0]
    # now the host leaves
    response = client.put(f"/game/1/player/{host.id}/leave")
    assert response.status_code == 200
    assert response.json() == {"message": "Partida 1 finalizada por el host"}
    try:
        game = game_crud.get_full_game(1)
    except Exception as e:
        assert e.args[0] == "Game[1]"
    finally:
        assert game.state == 3
