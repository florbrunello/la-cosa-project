import pytest
from fastapi.testclient import TestClient
from src.main import app
from pony.orm import db_session, rollback
from tests.test_setup import test_db, clear_db
from src.theThing.games import crud as game_crud
from src.theThing.games import schemas as game_schemas
from src.theThing.games.utils import assign_hands
from src.theThing.players import crud as player_crud
from src.theThing.players import schemas as player_schemas
from src.theThing.cards import crud as card_crud
from src.theThing.cards.schemas import CardCreate
from src.theThing.turn import crud as turn_crud
from src.theThing.turn import schemas as turn_schemas

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_module():
    # create a game
    game_data = game_schemas.GameCreate(
        name="Test Game finish", min_players=4, max_players=5
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
        code="def",
        name="Default",
        kind=0,
        description="Default card",
        number_in_card=1,
        playable=True,
    )

    extra_card = card_crud.create_card(extra_card_data, created_game.id)
    card_crud.give_card_to_player(
        extra_card.id, created_player.id, created_game.id
    )

    player_crud.update_player(
        player_schemas.PlayerUpdate(role=3), created_player.id, created_game.id
    )
    # set all other players to role =1
    for i in range(1, 5):
        player_crud.update_player(
            player_schemas.PlayerUpdate(role=1),
            players_in_game[i].id,
            created_game.id,
        )
    # finish setup
    yield


def test_finish_turn_game_not_started(test_db):
    # Test case 1: Game exists, but it is not started
    # finish the turn
    response = client.put("/turn/finish", json={"game_id": 1})
    assert response.status_code == 422
    assert response.json() == {"detail": "La partida aún no ha comenzado"}


def test_finish_turn_not_started(test_db):
    # Test case 2: Game exists, data is valid, and the game starts successfully
    game_crud.update_game(
        1,
        game_schemas.GameUpdate(state=1, play_direction=True, turn_owner=1),
    )
    turn_crud.create_turn(1, 1, "Player2")
    turn_crud.update_turn(1, turn_schemas.TurnCreate(state=1))
    # finish the turn
    response = client.put("/turn/finish", json={"game_id": 1})
    assert response.status_code == 422
    assert response.json() == {"detail": "El turno aún no ha terminado"}


def test_finish_turn_success(test_db):
    game = game_crud.get_full_game(1)
    turn_owener = [
        player
        for player in game.players
        if player.table_position == game.turn.owner
    ][0]
    # get card from player hand with kind != 5 or 3
    card = [card for card in turn_owener.hand if card.kind not in [3, 5]][0]
    discard_data = {
        "game_id": 1,
        "player_id": turn_owener.id,
        "card_id": card.id,
    }
    response = client.put("/game/discard", json=discard_data)
    game = game_crud.get_full_game(1)
    assert response.status_code == 200

    # pass exchange phase
    turn_crud.update_turn(
        1,
        turn_schemas.TurnCreate(
            state=5,
        ),
    )

    # finish the turn
    response = client.put("/turn/finish", json={"game_id": 1})
    assert response.status_code == 200
    assert response.json() == {
        "message": "Turno finalizado. Ahora el turno es de Player2",
    }


def test_finish_turn_1_end_case(test_db):
    # test case 3: The thing is eliminated, all humans win
    card_data2 = CardCreate(
        code="lla",
        name="Lanzallamas",
        kind=0,
        description="Lanzallamas",
        number_in_card=1,
        playable=True,
    )

    card = card_crud.create_card(card_data2, 1)
    turn_crud.update_turn(
        1,
        turn_schemas.TurnCreate(
            state=5,
            played_card=card.id,
            owner=2,
            destination_player="Player1",
            response_card=None,
        ),
    )

    actual_winners = ["Player2", "Player3", "Player4", "Player5"]
    response = client.put("/turn/finish", json={"game_id": 1})
    assert response.status_code == 200
    assert response.json()["message"] == "Partida finalizada"
    # check that each winner is inside the actual winners
    for winner in response.json()["winners"]:
        assert winner in actual_winners


def test_finish_turn_2_end_case(test_db):
    game = game_crud.update_game(1, game_schemas.GameUpdate(state=1))
    for i in range(2, 6):
        player_crud.update_player(
            player_schemas.PlayerUpdate(role=2, alive=True), i, 1
        )

    game = game_crud.update_game(1, game_schemas.GameUpdate(state=1))

    turn_crud.update_turn(1, turn_schemas.TurnCreate(state=5))

    response = client.put("/turn/finish", json={"game_id": 1})
    assert response.status_code == 200
    assert response.json()["message"] == "Partida finalizada"
    assert response.json()["winners"] == ["Player1"]
