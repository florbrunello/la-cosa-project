from fastapi.testclient import TestClient
from src.main import app
from pony.orm import db_session, rollback, commit
from .test_setup import test_db, clear_db
from src.theThing.games.crud import get_full_game, update_game, get_game
from src.theThing.turn.crud import update_turn
from src.theThing.turn.schemas import TurnCreate
from src.theThing.games.schemas import GameUpdate
from src.theThing.cards.schemas import CardCreate, CardUpdate
from src.theThing.cards.crud import create_card, delete_card, update_card
from src.theThing.players.crud import get_player

client = TestClient(app)


@db_session
def test_steal_card_success(test_db):
    # Test #1: steal a card from a player with valid data
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

    # Start the game
    game_data = {"game_id": 1, "player_name": "Test Host"}
    response = client.post("/game/start", json=game_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Partida 1 iniciada con éxito"}

    # Steal a card
    steal_data = {"game_id": 1, "player_id": 1}
    response = client.put("/game/steal", json=steal_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Carta robada con éxito"}
    game1 = get_game(1)
    player = get_player(1, 1)
    panic_codes = ["cac", "olv", "rev", "vyv"]
    panic_card = [
        card.code
        for card in player.hand
        if card.kind == 4 and card.code in panic_codes
    ]
    print(panic_card)
    if panic_card == []:
        assert game1.turn.state == 1
    else:
        assert game1.turn.state == 6
    # check if the player has a panic card


def test_steal_card_empty_deck(test_db):
    # Test #2: steal a card with empty deck

    # Update cards state to played in the previous game
    game = get_full_game(1)
    for card in game.deck:
        card_to_update = CardUpdate(id=card.id, state=0)
        update_card(card_to_update, 1)
    commit()

    gameupdate = GameUpdate(state=1, play_direction=True)
    update_game(1, gameupdate)
    commit()
    update_turn(1, TurnCreate(owner=2, state=0))
    # Steal a card. It should not generate any problems
    steal_data = {"game_id": 1, "player_id": 2}
    response = client.put("/game/steal", json=steal_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Carta robada con éxito"}


def test_steal_card_with_invalid_player_id(test_db):
    # Test #2: steal a card with invalid player id
    steal_data = {"game_id": 1, "player_id": 5}
    update_turn(1, TurnCreate(state=0))
    response = client.put("/game/steal", json=steal_data)
    assert response.status_code == 422
    assert response.json() == {"detail": "No se encontró el jugador"}


def test_steal_with_no_cards_indeck(test_db):
    # Test #2: steal a card from a player with no cards in deck
    # Delete the 31 cards on the previous test game to empty the deck
    game = get_full_game(1)
    for card in game.deck:
        response = delete_card(card.id, 1)
        assert response == {
            "message": f"Carta {card.id} eliminada con éxito de la partida 1"
        }
    commit()

    gameupdate = GameUpdate(state=1, play_direction=True)
    update_game(1, gameupdate)
    commit()
    update_turn(1, TurnCreate(owner=3, state=0))
    # Steal a card
    steal_data = {"game_id": 1, "player_id": 3}
    response = client.put("/game/steal", json=steal_data)
    assert response.status_code == 422
    assert response.json() == {"detail": "La carta no existe en el mazo"}


def test_steal_card_on_not_started_game(test_db):
    # Create a game first
    game_data = {
        "game": {"name": "Test Game 2", "min_players": 4, "max_players": 4},
        "host": {"name": "Test Host"},
    }
    client.post("/game/create", json=game_data)

    # Players data for joining
    join_data = {
        "players": [
            {"game_id": 2, "player_name": "Test Player 6"},
            {"game_id": 2, "player_name": "Test Player 7"},
            {"game_id": 2, "player_name": "Test Player 8"},
        ]
    }

    # Join players to the game
    playerid = 6
    for player in join_data["players"]:
        response = client.post("/game/join", json=player)
        assert response.status_code == 200
        assert response.json() == {
            "message": "El jugador se unió con éxito",
            "player_id": playerid,
            "game_id": 2,
        }
        playerid += 1

    update_turn(1, TurnCreate(state=0))
    # Steal a card
    steal_data = {"game_id": 2, "player_id": 5}
    response = client.put("/game/steal", json=steal_data)
    assert response.status_code == 422
    assert response.json() == {"detail": "La partida aún no ha comenzado"}


def test_steal_card_2_times(test_db):
    # Test: try to steal a card 2 times
    # start the previous game
    game_data = {"game_id": 2, "player_name": "Test Host"}
    response = client.post("/game/start", json=game_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Partida 2 iniciada con éxito"}

    # Steal a card
    steal_data = {"game_id": 2, "player_id": 5}
    update_turn(1, TurnCreate(state=0))
    response = client.put("/game/steal", json=steal_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Carta robada con éxito"}

    # Steal a card again
    steal_data = {"game_id": 2, "player_id": 5}
    response = client.put("/game/steal", json=steal_data)
    assert response.status_code == 422
    assert response.json() == {
        "detail": "No es posible robar una carta en este momento"
    }


def test_steal_card_with_empty_data():
    # Test #2: steal a card with empty data
    steal_data = {}
    response = client.put("/game/steal", json=steal_data)
    assert response.status_code == 422
    assert response.json() == {"detail": "La entrada no puede ser vacía"}


def test_steal_card_with_invalid_game_id(test_db):
    # Test #2: steal a card with invalid game id
    steal_data = {"game_id": 3, "player_id": 2}
    response = client.put("/game/steal", json=steal_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "No se encontró la partida"}
