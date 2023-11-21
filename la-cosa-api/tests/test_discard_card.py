import pytest
from .test_setup import test_db, clear_db
from src.theThing.cards import crud as card_crud
from src.theThing.cards.schemas import CardCreate, CardBase, CardUpdate
from src.theThing.games import crud as game_crud
from src.theThing.games.models import Game
from src.theThing.turn.crud import update_turn
from src.theThing.turn.schemas import TurnCreate
from src.theThing.games import schemas as game_schemas
from src.theThing.players import crud as player_crud
from src.theThing.players import schemas as player_schemas
from pony.orm import db_session, rollback, commit
from src.main import app
from fastapi.testclient import TestClient


client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_module():
    game_data = game_schemas.GameCreate(
        name="Test Game 1", min_players=4, max_players=5
    )
    created_game = game_crud.create_game(game_data)
    # create the owner player
    player_data = player_schemas.PlayerCreate(name="Player1", owner=True)
    created_player = player_crud.create_player(player_data, created_game.id)

    # create 3 players
    player_data = player_schemas.PlayerCreate(name="Player2", owner=False)
    created_player2 = player_crud.create_player(player_data, created_game.id)
    player_data = player_schemas.PlayerCreate(name="Player3", owner=False)
    created_player3 = player_crud.create_player(player_data, created_game.id)
    player_data = player_schemas.PlayerCreate(name="Player4", owner=False)
    created_player4 = player_crud.create_player(player_data, created_game.id)

    # start the game
    game_data = {"game_id": 1, "player_name": "Player1"}
    response = client.post("/game/start", json=game_data)
    assert response.status_code == 200
    # update turn state
    update_turn(1, TurnCreate(state=0))


def test_discard_card_succesfully(test_db):
    # Test #1: discard card succesfully
    # Steal a card
    steal_data = {"game_id": 1, "player_id": 1}
    response = client.put("/game/steal", json=steal_data)
    assert response.status_code == 200

    # get a random card from the player hand
    player = player_crud.get_player(1, 1)
    card = [card for card in player.hand if card.kind not in [3, 5]][0]
    # Discard a random card
    discard_data = {"game_id": 1, "player_id": 1, "card_id": card.id}
    response = client.put("/game/discard", json=discard_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Carta descartada con éxito"}
    game1 = game_crud.get_game(1)
    assert game1.turn.state == 3


def test_discard_wrong_game(test_db):
    # Test #2: discard card with wrong game
    update_turn(1, TurnCreate(state=0, owner=2))

    # Steal a card
    steal_data = {"game_id": 1, "player_id": 2}
    response = client.put("/game/steal", json=steal_data)
    assert response.status_code == 200

    # get a random card from the player hand
    player = player_crud.get_player(2, 1)
    # Discard a random card
    card = [card for card in player.hand if card.kind not in [3, 5]][0]
    discard_data = {"game_id": 2, "player_id": 2, "card_id": card.id}
    response = client.put("/game/discard", json=discard_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "No se encontró la partida"}


def test_discard_without_stealing(test_db):
    # Test #3: discard card without stealing first
    update_turn(1, TurnCreate(state=1, owner=3))

    # get a random card from the player hand
    player = player_crud.get_player(3, 1)
    # Discard a random card
    card = [card for card in player.hand if card.kind not in [3, 5]][0]
    discard_data = {"game_id": 1, "player_id": 3, "card_id": card.id}
    response = client.put("/game/discard", json=discard_data)
    assert response.status_code == 422
    assert response.json() == {
        "detail": "No es posible descartar sin robar una carta primero"
    }


def test_discard_2_times(test_db):
    # Test #4: discard card 2 times in a row
    update_turn(1, TurnCreate(state=0, owner=4))

    steal_data = {"game_id": 1, "player_id": 4}
    response = client.put("/game/steal", json=steal_data)
    assert response.status_code == 200
    # get a random card from the player hand
    player = player_crud.get_player(4, 1)
    # Discard a random card
    card = [card for card in player.hand if card.kind not in [3, 5, 6]][0]
    discard_data = {"game_id": 1, "player_id": 4, "card_id": card.id}
    response = client.put("/game/discard", json=discard_data)
    assert response.status_code == 200

    game1 = game_crud.get_game(1)
    assert game1.turn.state == 3

    player = player_crud.get_player(4, 1)
    card = [card for card in player.hand if card.kind not in [3, 5, 6]][0]
    discard_data = {"game_id": 1, "player_id": 4, "card_id": card.id}
    response = client.put("/game/discard", json=discard_data)
    assert response.status_code == 422
    assert response.json() == {
        "detail": "No es posible descartar en este momento"
    }


def test_discard_not_existent_card(test_db):
    # Test #5: discard card that doesn't exist in the player's hand
    update_turn(1, TurnCreate(state=0, owner=1))

    # steal a card
    steal_data = {"game_id": 1, "player_id": 1}
    response = client.put("/game/steal", json=steal_data)
    assert response.status_code == 200

    # get a card id which is not in the player's hand, but exists in the game
    player = player_crud.get_player(2, 1)
    card = [card for card in player.hand if card.kind not in [3, 5]][0]

    discard_data = {"game_id": 1, "player_id": 1, "card_id": card.id}
    response = client.put("/game/discard", json=discard_data)
    assert response.status_code == 422
    assert response.json() == {
        "detail": "La carta no pertenece a la mano del jugador o al mazo de la partida"
    }
