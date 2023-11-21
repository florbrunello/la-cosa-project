import pytest

from .test_setup import test_db, clear_db
from src.theThing.cards import crud as card_crud
from src.theThing.cards.schemas import CardCreate, CardBase, CardUpdate
from src.theThing.games import crud as game_crud
from src.theThing.games.models import Game
from src.theThing.games import schemas as game_schemas
from src.theThing.players import crud as player_crud
from src.theThing.players import schemas as player_schemas
from src.theThing.turn import crud as turn_crud
from src.theThing.turn import schemas as turn_schemas
from pony.orm import db_session, rollback, commit
from src.main import app
from fastapi.testclient import TestClient

# create pytest fixture that runs once for the module before this tests

client = TestClient(app)


@pytest.fixture(scope="module")
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
    player_data = player_schemas.PlayerCreate(name="Player5", owner=False)
    created_player5 = player_crud.create_player(player_data, created_game.id)

    players_in_game = [
        created_player,
        created_player2,
        created_player3,
        created_player4,
        created_player5,
    ]
    # create 3 cards for each player
    card_data = CardCreate(
        code="def",
        name="Default",
        kind=0,
        description="This is a default card",
        number_in_card=1,
        playable=True,
    )
    for i in range(4):
        created_card = card_crud.create_card(card_data, created_game.id)
        created_card2 = card_crud.create_card(card_data, created_game.id)
        created_card3 = card_crud.create_card(card_data, created_game.id)

        # add the card to the player hand
        card_crud.give_card_to_player(
            created_card.id, players_in_game[i].id, created_game.id
        )
        card_crud.give_card_to_player(
            created_card2.id, players_in_game[i].id, created_game.id
        )
        card_crud.give_card_to_player(
            created_card3.id, players_in_game[i].id, created_game.id
        )

    card_data2 = CardCreate(
        code="lla",
        name="Lanzallamas",
        kind=0,
        description="Lanzallamas",
        number_in_card=1,
        playable=True,
    )
    for i in range(4):
        created_card = card_crud.create_card(card_data2, created_game.id)

        card_crud.give_card_to_player(
            created_card.id, players_in_game[i].id, created_game.id
        )

    # give an extra card to the owner
    extra_card_data = CardCreate(
        code="ext",
        name="Extra",
        kind=0,
        description="Extra",
        number_in_card=1,
        playable=False,
    )

    extra_card = card_crud.create_card(extra_card_data, created_game.id)
    card_crud.give_card_to_player(
        extra_card.id, created_player.id, created_game.id
    )

    # start the game
    game_crud.update_game(
        created_game.id,
        game_schemas.GameUpdate(state=1, play_direction=True, turn_owner=1),
    )
    turn_crud.create_turn(created_game.id, 1, "Player2")
    turn_crud.update_turn(created_game.id, turn_schemas.TurnCreate(state=1))
    # finish setup
    yield


# test case 1: player destination is the player itself
@db_session
def test_play_card_itself(setup_module):
    response = client.put(
        "/game/play",
        json={
            "game_id": 1,
            "player_id": 1,
            "card_id": 1,
            "destination_name": "Player1",
        },
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": "No se puede aplicar el efecto a sí mismo"
    }

    rollback()  # rollback the changes made in the database


# test case 2: player is not the turn owner
@db_session
def test_play_card_not_turn_owner(setup_module):
    response = client.put(
        "/game/play",
        json={
            "game_id": 1,
            "player_id": 2,
            "card_id": 1,
            "destination_name": "Player1",
        },
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": "No es el turno del jugador especificado"
    }

    rollback()


# test case 3: card is not in the player hand
@db_session
def test_play_card_not_in_hand(setup_module):
    response = client.put(
        "/game/play",
        json={
            "game_id": 1,
            "player_id": 1,
            "card_id": 5,
            "destination_name": "Player2",
        },
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": "La carta no pertenece a la mano del jugador o al mazo de la partida"
    }

    rollback()


# test case 4: card is not playable
@db_session
def test_play_card_not_playable(setup_module):
    response = client.put(
        "/game/play",
        json={
            "game_id": 1,
            "player_id": 1,
            "card_id": 17,
            "destination_name": "Player2",
        },
    )
    assert response.status_code == 422
    assert response.json() == {"detail": "La carta seleccionada no es jugable"}

    rollback()


# test case 5: the destination player is not adjacent to the player
@db_session
def test_play_card_not_adjacent(setup_module):
    response = client.put(
        "/game/play",
        json={
            "game_id": 1,
            "player_id": 1,
            "card_id": 1,
            "destination_name": "Player3",
        },
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": "El jugador destino no está sentado en una posición adyacente"
    }

    rollback()


# test case 6: the card is played correctly
@db_session
def test_play_card(setup_module):
    response = client.put(
        "/game/play",
        json={
            "game_id": 1,
            "player_id": 1,
            "card_id": 1,
            "destination_name": "Player2",
        },
    )
    assert response.status_code == 200

    player2_status = player_crud.get_player(2, 1)
    assert player2_status.alive == True  # because the card is not a kill card
    card_played_status = card_crud.get_card(1, 1)
    assert card_played_status.state == 0  # because the card is played

    game = game_crud.get_game(1)

    assert game.turn == turn_schemas.TurnOut(
        owner=1,
        played_card=card_played_status,
        destination_player="Player2",
        destination_player_exchange="Player2",
        response_card=None,
        state=2,
    )


# test case 7: the player cant play because does not have enough cards
@db_session
def test_play_card_not_enough_cards(setup_module):
    # set back the turn to state 1 to allow the player to play
    turn_crud.update_turn(1, turn_schemas.TurnCreate(state=1))
    commit()
    response = client.put(
        "/game/play",
        json={
            "game_id": 1,
            "player_id": 1,
            "card_id": 2,
            "destination_name": "Player2",
        },
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": "El jugador tiene menos cartas de las necesarias para jugar"
    }
