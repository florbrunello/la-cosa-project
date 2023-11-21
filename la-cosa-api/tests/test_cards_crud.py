from .test_setup import test_db, clear_db
from src.theThing.cards import crud as card_crud
from src.theThing.cards.schemas import CardCreate, CardBase, CardUpdate
from src.theThing.games import crud as game_crud
from src.theThing.games import schemas as game_schemas
from src.theThing.players import crud as player_crud
from src.theThing.players import schemas as player_schemas
from pony.orm import db_session, rollback, ObjectNotFound


@db_session
def test_create_and_get_card(test_db):
    # First create a game where to add the card
    game_data = game_schemas.GameCreate(
        name="Test Game deck", min_players=2, max_players=4
    )
    created_game = game_crud.create_game(game_data)

    # Create a card
    card_data = CardCreate(
        code="test_code",
        name="Test Card",
        kind=0,
        description="This is a test card",
        number_in_card=1,
        playable=True,
    )

    created_card = card_crud.create_card(card_data, created_game.id)

    assert created_card.model_dump() == {
        "id": 1,
        "code": "test_code",
        "name": "Test Card",
        "kind": 0,
        "description": "This is a test card",
        "number_in_card": 1,
        "state": 2,
        "playable": True,
    }

    # Get the card
    retrieved_card = card_crud.get_card(created_card.id, created_game.id)
    assert retrieved_card == created_card

    rollback()


@db_session
def test_create_wrong_card(test_db):
    # First create a game where to add the card
    game_data = game_schemas.GameCreate(
        name="Test Game deck", min_players=2, max_players=4
    )
    created_game = game_crud.create_game(game_data)

    # Create a card
    card_data = CardCreate(
        code="test_code",
        name="Test Card",
        kind=7,
        description="This is a test card",
        number_in_card=1,
        playable=True,
    )

    try:
        created_card = card_crud.create_card(card_data, created_game.id)
    except ValueError as e:
        assert e.args[0] == "The kind of the card is not valid"

    rollback()


@db_session
def test_player_hand(test_db):
    game_data = game_schemas.GameCreate(
        name="Test Game deck", min_players=2, max_players=4
    )
    created_game = game_crud.create_game(game_data)

    cards_data = [
        CardCreate(
            code="test_code0",
            name="Test Card0",
            kind=0,
            description="This is a test card0",
            number_in_card=1,
            playable=True,
        ),
        CardCreate(
            code="test_code1",
            name="Test Card1",
            kind=1,
            description="This is a test card1",
            number_in_card=1,
            playable=True,
        ),
        CardCreate(
            code="test_code2",
            name="Test Card2",
            kind=2,
            description="This is a test card2",
            number_in_card=1,
            playable=True,
        ),
    ]
    created_card1 = card_crud.create_card(cards_data[0], created_game.id)
    created_card2 = card_crud.create_card(cards_data[1], created_game.id)
    created_card3 = card_crud.create_card(cards_data[2], created_game.id)

    # add a player to the game
    created_player = player_crud.create_player(
        player_schemas.PlayerCreate(name="Test Player", owner=True),
        created_game.id,
    )

    # add the cards to the player
    card_crud.give_card_to_player(
        created_card1.id, created_player.id, created_game.id
    )
    card_crud.give_card_to_player(
        created_card2.id, created_player.id, created_game.id
    )

    player_data = player_crud.get_player(created_player.id, created_game.id)
    expected_cards = [
        CardBase(
            **{
                "id": 1,
                "code": "test_code0",
                "name": "Test Card0",
                "kind": 0,
                "description": "This is a test card0",
                "number_in_card": 1,
                "state": 1,
                "playable": True,
            }
        ),
        CardBase(
            **{
                "id": 2,
                "code": "test_code1",
                "name": "Test Card1",
                "kind": 1,
                "description": "This is a test card1",
                "number_in_card": 1,
                "state": 1,
                "playable": True,
            }
        ),
    ]
    assert [card in player_data.hand for card in expected_cards]

    rollback()


@db_session
def test_add_card_wrong_player(test_db):
    # First create a game where to add the card
    game_data = game_schemas.GameCreate(
        name="Test Game deck1", min_players=2, max_players=4
    )
    created_game = game_crud.create_game(game_data)
    # Create a card
    card_data = CardCreate(
        code="test_code",
        name="Test Card",
        kind=0,
        description="This is a test card",
        number_in_card=1,
        playable=True,
    )

    created_card1 = card_crud.create_card(card_data, created_game.id)
    # add a player to the game
    created_player = player_crud.create_player(
        player_schemas.PlayerCreate(name="Test Player", owner=True),
        created_game.id,
    )

    try:
        card_crud.give_card_to_player(
            created_card1.id, created_player.id + 1, created_game.id
        )
    except Exception as e:
        assert e.args[0] == f"No se encontró el jugador"

    rollback()


@db_session
def test_delete_card(test_db):
    game_data = game_schemas.GameCreate(
        name="Test Game deck", min_players=2, max_players=4
    )
    created_game = game_crud.create_game(game_data)
    created_card = card_crud.create_card(
        CardCreate(
            code="test_code",
            name="Test Card",
            kind=0,
            description="This is a test card",
            number_in_card=1,
            playable=True,
        ),
        created_game.id,
    )

    card_crud.delete_card(created_card.id, created_game.id)

    try:
        card_crud.get_card(created_card.id, created_game.id)
    except ObjectNotFound as e:
        assert e.args[0] == f"Card[{created_card.id}]"

    rollback()


@db_session
def test_update_card_state(test_db):
    game_data = game_schemas.GameCreate(
        name="Test Game deck", min_players=2, max_players=4
    )

    created_game = game_crud.create_game(game_data)
    created_card = card_crud.create_card(
        CardCreate(
            code="test_code",
            name="Test Card",
            kind=0,
            description="This is a test card",
            number_in_card=1,
            playable=True,
        ),
        created_game.id,
    )

    assert created_card.state == 2

    updated_card = card_crud.update_card(
        CardUpdate(id=created_card.id, state=1), created_game.id
    )

    assert updated_card.state == 1
