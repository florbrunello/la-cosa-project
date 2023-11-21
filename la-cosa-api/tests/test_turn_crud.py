import pytest
from pony.orm import db_session, rollback, ObjectNotFound

from src.theThing.games import crud as game_crud
from src.theThing.games.schemas import GameCreate, GameOut
from src.theThing.turn import crud
from src.theThing.turn.schemas import TurnCreate, TurnOut
from .test_setup import test_db, clear_db
from src.theThing.cards import crud as card_crud


def test_create_turn(test_db):
    game_data = GameCreate(name="Test Game", min_players=4, max_players=6)
    created_game = game_crud.create_game(game_data)

    created_turn = crud.create_turn(created_game.id, 1, "")

    assert created_turn.owner == 1
    assert game_crud.get_game(created_game.id).model_dump() == {
        "id": 1,
        "name": "Test Game",
        "min_players": 4,
        "max_players": 6,
        "state": 0,
        "play_direction": True,
        "obstacles": [],
        "turn": {
            "destination_player": "",
            "destination_player_exchange": "",
            "owner": 1,
            "played_card": None,
            "response_card": None,
            "state": 0,
        },
        "players": [],
    }


def test_update_turn(test_db):
    # start the game first to creat the deck
    game_crud.create_game_deck(1, 4)
    updated_turn = crud.update_turn(
        1,
        TurnCreate(
            owner=1,
            played_card=1,
            destination_player="TestPlayer1",
            response_card=3,
            state=1,
        ),
    )
    card = card_crud.get_card(1, 1)
    response_card = card_crud.get_card(3, 1)
    assert updated_turn.owner == 1
    assert updated_turn.played_card == 1
    assert updated_turn.destination_player == "TestPlayer1"
    assert updated_turn.response_card == 3
    assert updated_turn.state == 1
    assert game_crud.get_game(1).model_dump() == {
        "id": 1,
        "name": "Test Game",
        "min_players": 4,
        "max_players": 6,
        "state": 0,  # its 0 because the game is not started (because we never called the endpoint)
        "play_direction": True,
        "obstacles": [],
        "turn": {
            "destination_player": "TestPlayer1",
            "destination_player_exchange": "",
            "owner": 1,
            "played_card": card.model_dump(),
            "response_card": response_card.model_dump(),
            "state": 1,
        },
        "players": [],
    }
