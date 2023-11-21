import pytest
from .test_setup import test_db, clear_db
from fastapi.testclient import TestClient
from src.main import app
from pony.orm import db_session, rollback, flush
from src.theThing.games import crud as game_crud
from src.theThing.games import schemas as game_schemas
from src.theThing.players import crud as player_crud
from src.theThing.players import schemas as player_schemas
from src.theThing.cards import crud as card_crud
from src.theThing.cards.schemas import CardCreate
from src.theThing.turn import crud as turn_crud
from src.theThing.turn import schemas as turn_schemas

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_test():
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

    turn_crud.update_turn(1, turn_schemas.TurnCreate(state=3))
    # Give an extra card to the player
    card_data = CardCreate(
        code="sos",
        name="Sospecha",
        kind=0,
        description="Mira una carta aleatoria de la mano de un jugador adyacente.",
        number_in_card=4,
        playable=True,
    )
    card_created = card_crud.create_card(card_data, 1)
    card_crud.give_card_to_player(card_created.id, 1, 1)
    flush()


def test_exchange_success(test_db):
    # Test #1: exchange with an obstacle
    # Get a card from the player hand
    player = player_crud.get_player(1, 1)
    card = [card for card in player.hand if card.kind not in [3, 5]][0]
    exchange_data = {"game_id": 1, "player_id": 1, "card_id": card.id}
    response = client.put("/game/exchange", json=exchange_data)
    assert response.status_code == 200
    assert response.json() == {
        "message": "Ofrecimiento de intercambio realizado"
    }
    # Accept exchange
    destination_player = player_crud.get_player(2, 1)
    # Get a card from the destination player hand
    response_card = [
        card for card in destination_player.hand if card.kind not in [3, 5]
    ][0]
    response_exchange_data = {
        "game_id": 1,
        "defending_player_id": 2,
        "exchange_card_id": response_card.id,
        "defense_card_id": None,
    }
    response = client.put(
        "/game/response-exchange", json=response_exchange_data
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Intercambio finalizado"}
    # Check the cards were swapped between players
    player = player_crud.get_player(1, 1)
    destination_player = player_crud.get_player(2, 1)
    assert (card not in player.hand) and card in destination_player.hand
    assert (
        response_card not in destination_player.hand
    ) and response_card in player.hand
    # finish the turn
    response = client.put("/turn/finish", json={"game_id": 1})
    assert response.status_code == 200


def test_exchange_with_obstacle(test_db):
    # Test #2: exchange with an obstacle
    # Update game with an obstacle
    game_crud.update_game(1, game_schemas.GameUpdate(obstacles=[2]))
    turn_crud.update_turn(1, turn_schemas.TurnCreate(state=3))
    # Give an extra card to the player
    card_data = CardCreate(
        code="sos",
        name="Sospecha",
        kind=0,
        description="Mira una carta aleatoria de la mano de un jugador adyacente.",
        number_in_card=4,
        playable=True,
    )
    card_created = card_crud.create_card(card_data, 1)
    card_crud.give_card_to_player(card_created.id, 1, 1)
    flush()

    # Get a card from the player hand
    player = player_crud.get_player(2, 1)
    card = [card for card in player.hand if card.kind not in [3, 5]][0]
    exchange_data = {"game_id": 1, "player_id": 2, "card_id": card.id}
    response = client.put("/game/exchange", json=exchange_data)
    assert response.status_code == 200
    assert response.json() == {
        "message": "Existe una puerta atrancada. Se saltea el intercambio"
    }
    # finish the turn
    response = client.put("/turn/finish", json={"game_id": 1})
    assert response.status_code == 200


def test_exchange_defense_ngs(test_db):
    # Test #3: exchange but the destination player defense from it
    turn_crud.update_turn(1, turn_schemas.TurnCreate(state=0))
    # Give an extra card to the next player
    card_data = CardCreate(
        code="ngs",
        name="¡No, gracias!",
        kind=1,
        description="Niégate a un ofrecimiento de intercambio de cartas.",
        number_in_card=4,
        playable=True,
    )
    card_created = card_crud.create_card(card_data, 1)
    # Get a card from destination_player_to_exchange hand to replace it with the defense card
    destination_player = player_crud.get_player(4, 1)
    card_to_delete = [
        card for card in destination_player.hand if card.kind not in [3, 5]
    ][0]
    card_crud.delete_card(card_to_delete.id, 1)
    card_created = card_crud.give_card_to_player(card_created.id, 4, 1)
    flush()
    # Steal a card
    steal_data = {"game_id": 1, "player_id": 3}
    response = client.put("/game/steal", json=steal_data)
    assert response.status_code == 200
    turn_crud.update_turn(1, turn_schemas.TurnCreate(state=3))
    flush()
    # Get a card from the turn owner
    exchange_offerer = player_crud.get_player(3, 1)
    offered_card = [
        card for card in exchange_offerer.hand if card.kind not in [3, 5]
    ][0]
    exchange_data = {"game_id": 1, "player_id": 3, "card_id": offered_card.id}
    response = client.put("/game/exchange", json=exchange_data)
    assert response.status_code == 200
    assert response.json() == {
        "message": "Ofrecimiento de intercambio realizado"
    }
    # Response exchange
    response_exchange_data = {
        "game_id": 1,
        "defending_player_id": 4,
        "exchange_card_id": None,
        "defense_card_id": card_created.id,
    }
    response = client.put(
        "/game/response-exchange", json=response_exchange_data
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Intercambio finalizado"}
    # Check that the cards were not swapped
    exchange_offerer = player_crud.get_player(3, 1)
    destination_player = player_crud.get_player(4, 1)
    assert (
        offered_card in exchange_offerer.hand
        and offered_card not in destination_player.hand
    )
    assert (
        card_created not in exchange_offerer.hand
        and card_created not in destination_player.hand
    )
    # finish the turn
    response = client.put("/turn/finish", json={"game_id": 1})
    assert response.status_code == 200
