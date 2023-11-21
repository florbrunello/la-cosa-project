import pytest
from src.theThing.games import crud as games_crud
from src.theThing.games import schemas as games_schemas
from src.theThing.players import crud as players_crud
from src.theThing.players import schemas as players_schemas
from src.theThing.cards.effect_applications import (
    effect_applications as cards_effect_applications,
)
from src.theThing.cards.special_effect_applications import *
from src.theThing.cards import crud as cards_crud
from src.theThing.cards import schemas as cards_schemas
from src.theThing.turn import crud as turn_crud
from src.theThing.turn import schemas as turn_schemas
from src.main import app
from fastapi.testclient import TestClient
from tests.test_setup import test_db, clear_db

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_module():
    # create a game, add 4 players and create a turn
    game_data = games_schemas.GameCreate(
        name="Test Game deck", min_players=4, max_players=5
    )
    created_game = games_crud.create_game(game_data)
    # create the owner player
    player_data = players_schemas.PlayerCreate(name="Player1", owner=True)
    created_player = players_crud.create_player(player_data, created_game.id)

    # create 3 players
    player_data = players_schemas.PlayerCreate(name="Player2", owner=False)
    created_player2 = players_crud.create_player(player_data, created_game.id)
    player_data = players_schemas.PlayerCreate(name="Player3", owner=False)
    created_player3 = players_crud.create_player(player_data, created_game.id)
    player_data = players_schemas.PlayerCreate(name="Player4", owner=False)
    created_player4 = players_crud.create_player(player_data, created_game.id)
    created_player4 = players_crud.update_player(
        players_schemas.PlayerUpdate(role=3),
        created_player4.id,
        created_game.id,
    )
    # create a turn, owner is player 1, exchange destination is player 2
    turn_crud.create_turn(created_game.id, 1, created_player2.name)

    # start the game to have a deck
    client.post("/game/start", json={"game_id": 1, "player_name": "Player1"})

    # set turn to state 1 (deciding)
    turn_data = turn_schemas.TurnCreate(state=1)
    turn_crud.update_turn(created_game.id, turn_data)


@pytest.mark.asyncio
async def test_lla(test_db):
    # this card kills the destination player
    card = cards_schemas.CardCreate(
        code="lla",
        name="Lanzallamas",
        kind=0,
        description="Lanzallamas",
        number_in_card=1,
        playable=True,
    )
    card = cards_crud.create_card(card, 1)
    full_game = games_crud.get_full_game(1)
    player = players_crud.get_player(1, 1)
    destination_player = players_crud.get_player(2, 1)
    game, message = await cards_effect_applications[card.code](
        full_game, player, destination_player, card
    )

    updated_card = cards_crud.get_card(card.id, 1)
    updated_d_player = players_crud.get_player(2, 1)

    assert updated_card.state == 0
    assert updated_d_player.alive == False
    assert game.turn.destination_player_exchange == "Player3"


@pytest.mark.asyncio
async def test_vte(test_db):
    card = cards_schemas.CardCreate(
        code="vte",
        name="Vigila tus espaldas",
        kind=0,
        description="Vigila tus espaldas",
        number_in_card=1,
        playable=True,
    )
    card = cards_crud.create_card(card, 1)
    full_game = games_crud.get_full_game(1)
    player = players_crud.get_player(1, 1)

    game, message = await cards_effect_applications[card.code](
        full_game, player, player, card
    )

    updated_card = cards_crud.get_card(card.id, 1)
    assert updated_card.state == 0
    assert game.turn.destination_player_exchange == "Player4"
    assert game.play_direction != full_game.play_direction


@pytest.mark.asyncio
async def test_cdl(clear_db):
    card = cards_schemas.CardCreate(
        code="cdl",
        name="Cambio de lugar",
        kind=0,
        description="Cambio de lugar",
        number_in_card=1,
        playable=True,
    )
    card = cards_crud.create_card(card, 1)
    full_game = games_crud.get_full_game(1)
    player = players_crud.get_player(1, 1)
    player_tb = player.table_position
    destination_player = players_crud.get_player(3, 1)
    destination_player_tb = destination_player.table_position
    game, message = await cards_effect_applications[card.code](
        full_game, player, destination_player, card
    )

    updated_card = cards_crud.get_card(card.id, 1)
    updated_player = players_crud.get_player(1, 1)
    updated_d_player = players_crud.get_player(3, 1)

    assert updated_card.state == 0
    assert updated_player.table_position == destination_player_tb
    assert updated_d_player.table_position == player_tb
    assert game.turn.destination_player_exchange == "Player3"


@pytest.mark.asyncio
async def test_mvc(clear_db):
    # this card does the same as cdl
    card = cards_schemas.CardCreate(
        code="mvc",
        name="Mas vale que corras",
        kind=0,
        description="Mas vale que corras",
        number_in_card=1,
        playable=True,
    )
    card = cards_crud.create_card(card, 1)
    full_game = games_crud.get_full_game(1)
    player = players_crud.get_player(1, 1)
    player_tb = player.table_position
    destination_player = players_crud.get_player(4, 1)
    destination_player_tb = destination_player.table_position

    game, message = await cards_effect_applications[card.code](
        full_game, player, destination_player, card
    )

    updated_card = cards_crud.get_card(card.id, 1)
    updated_player = players_crud.get_player(1, 1)
    updated_d_player = players_crud.get_player(4, 1)

    assert updated_card.state == 0
    assert updated_player.table_position == destination_player_tb
    assert updated_d_player.table_position == player_tb
    assert game.turn.destination_player_exchange == "Player4"


@pytest.mark.asyncio
async def test_cua(test_db):
    card = cards_schemas.CardCreate(
        code="cua",
        name="Cuarentena",
        kind=0,
        description="Cuarentena",
        number_in_card=1,
        playable=True,
    )
    card = cards_crud.create_card(card, 1)
    full_game = games_crud.get_full_game(1)
    player = players_crud.get_player(1, 1)
    destination_player = players_crud.get_player(3, 1)

    game, message= await cards_effect_applications[card.code](
        full_game, player, destination_player, card
    )

    updated_card = cards_crud.get_card(card.id, 1)
    updated_d_player = players_crud.get_player(3, 1)

    assert updated_card.state == 0
    assert updated_d_player.quarantine == 2


@pytest.mark.asyncio
async def test_cpo(test_db):
    # set all players in quarantine, revive all players and order assign new table positions
    players_crud.update_player(
        players_schemas.PlayerUpdate(quarantine=2, table_position=1), 1, 1
    )
    players_crud.update_player(
        players_schemas.PlayerUpdate(
            quarantine=2, alive=True, table_position=2
        ),
        2,
        1,
    )
    players_crud.update_player(
        players_schemas.PlayerUpdate(
            quarantine=2, alive=True, table_position=3
        ),
        3,
        1,
    )
    players_crud.update_player(
        players_schemas.PlayerUpdate(
            quarantine=2, alive=True, table_position=4
        ),
        4,
        1,
    )

    card = cards_schemas.CardCreate(
        code="cpo",
        name="Cuerdas podridas",
        kind=4,
        description="Cuerdas podridas",
        number_in_card=1,
        playable=True,
    )

    card = cards_crud.create_card(card, 1)
    full_game = games_crud.get_full_game(1)
    player = players_crud.get_player(1, 1)

    game, message = await cards_effect_applications[card.code](
        full_game, player, player, card
    )

    updated_card = cards_crud.get_card(card.id, 1)
    assert updated_card.state == 0
    for player in game.players:
        assert player.quarantine == 0


@pytest.mark.asyncio
async def test_und(test_db):
    card = cards_schemas.CardCreate(
        code="und",
        name="Uno,dos",
        kind=4,
        description="Uno,dos",
        number_in_card=1,
        playable=True,
    )
    card = cards_crud.create_card(card, 1)
    full_game = games_crud.get_full_game(1)
    player = players_crud.get_player(1, 1)
    player_tb = player.table_position
    destination_player = players_crud.get_player(3, 1)
    destination_player_tb = destination_player.table_position
    game, message = await cards_effect_applications[card.code](
        full_game, player, destination_player, card
    )

    updated_card = cards_crud.get_card(card.id, 1)
    updated_player = players_crud.get_player(1, 1)
    updated_d_player = players_crud.get_player(3, 1)

    assert updated_card.state == 0
    assert updated_player.table_position == destination_player_tb
    assert updated_d_player.table_position == player_tb
    # game direction is not going clockwise
    assert game.turn.destination_player_exchange == "Player2"
    # the positions are [player3, player2, player1, player4]


@pytest.mark.asyncio
async def test_sda(test_db):
    card = cards_schemas.CardCreate(
        code="sda",
        name="Sal de aqui",
        kind=4,
        description="Sal de aqui",
        number_in_card=1,
        playable=True,
    )
    card = cards_crud.create_card(card, 1)
    full_game = games_crud.get_full_game(1)
    player = players_crud.get_player(1, 1)
    player_tb = player.table_position
    destination_player = players_crud.get_player(2, 1)
    destination_player_tb = destination_player.table_position

    game, message = await cards_effect_applications[card.code](
        full_game, player, destination_player, card
    )

    updated_card = cards_crud.get_card(card.id, 1)
    updated_player = players_crud.get_player(1, 1)
    updated_d_player = players_crud.get_player(2, 1)

    assert updated_card.state == 0
    assert updated_player.table_position == destination_player_tb
    assert updated_d_player.table_position == player_tb
    assert game.turn.destination_player_exchange == "Player3"
    game.players.sort(key=lambda x: x.table_position)
    name_o_players = [player.name for player in game.players]
    assert name_o_players == ["Player3", "Player1", "Player2", "Player4"]
    # the positions are [player3, player1, player2, player4]


@pytest.mark.asyncio
async def test_trc(test_db):
    card = cards_schemas.CardCreate(
        code="trc",
        name="Tres, cuatro",
        kind=4,
        description="Tres, cuatro",
        number_in_card=1,
        playable=True,
    )
    card = cards_crud.create_card(card, 1)
    game = games_crud.get_full_game(1)
    game.obstacles.append(1)
    game.obstacles.append(2)
    games_crud.update_game(
        1, games_schemas.GameUpdate(obstacles=game.obstacles)
    )
    full_game = games_crud.get_full_game(1)
    player = players_crud.get_player(1, 1)

    game, message = await cards_effect_applications[card.code](
        full_game, player, player, card
    )

    updated_card = cards_crud.get_card(card.id, 1)
    assert updated_card.state == 0
    assert game.obstacles == []


@pytest.mark.asyncio
async def test_eaf(test_db):
    card = cards_schemas.CardCreate(
        code="eaf",
        name="¿Es aqui la fiesta?",
        kind=4,
        description="¿Es aqui la fiesta?",
        number_in_card=1,
        playable=True,
    )
    card = cards_crud.create_card(card, 1)

    game = games_crud.get_full_game(1)
    game.obstacles.append(1)
    game.obstacles.append(2)
    games_crud.update_game(
        1, games_schemas.GameUpdate(obstacles=game.obstacles)
    )
    full_game = games_crud.get_full_game(1)
    owner_tb = full_game.turn.owner
    owner_player = [
        player
        for player in full_game.players
        if player.table_position == owner_tb
    ][0]

    game, message = await cards_effect_applications[card.code](
        full_game, owner_player, owner_player, card
    )
    # the positions are [player1, player3, player4, player2]
    card = cards_crud.get_card(card.id, 1)
    assert card.state == 0
    assert game.obstacles == []
    game.players.sort(key=lambda x: x.table_position)
    name_o_players = [player.name for player in game.players]
    assert name_o_players == ["Player4", "Player2", "Player1", "Player3"]


@pytest.mark.asyncio
async def test_ptr(test_db):
    card = cards_schemas.CardCreate(
        code="ptr",
        name="Puerta atrancada",
        kind=2,
        description="Puerta atrancada",
        number_in_card=1,
        playable=True,
    )
    card = cards_crud.create_card(card, 1)

    game = games_crud.get_full_game(1)
    full_game = games_crud.get_full_game(1)
    player = players_crud.get_player(1, 1)
    destination_player = players_crud.get_player(3, 1)
    # the positions are [('Player4', 1), ('Player2', 2), ('Player1', 3), ('Player3', 4)]
    # if Player1 puts a ptr to player 3, then the position 3 goes in the obstacle list
    await cards_effect_applications[card.code](
        full_game, player, destination_player, card
    )

    updated_card = cards_crud.get_card(card.id, 1)
    game = games_crud.get_full_game(1)
    assert updated_card.state == 0
    assert game.obstacles == [3]


@pytest.mark.asyncio
async def test_cac(test_db):
    card = cards_schemas.CardCreate(
        code="cac",
        name="Cita a ciegas",
        kind=4,
        description="Cita a ciegas",
        number_in_card=1,
        playable=True,
    )

    default_card = cards_schemas.CardCreate(
        code="def",
        name="default",
        kind=0,
        description="default",
        number_in_card=1,
        playable=True,
    )
    card = cards_crud.create_card(card, 1)
    default_card = cards_crud.create_card(default_card, 1)
    cards_crud.give_card_to_player(default_card.id, 1, 1)
    full_game = games_crud.get_full_game(1)
    player = players_crud.get_player(1, 1)
    player_hand = player.hand[0]

    data = {
        "game_id": 1,
        "player_id": 1,
        "card_id": default_card.id,
        "panic_card_id": card.id,
    }
    try:
        player, game = await apply_cac(data)
    except Exception as e:
        raise e
    cac_card = cards_crud.get_card(card.id, 1)
    def_card = cards_crud.get_card(default_card.id, 1)

    # assert cac_card.state == 0
    assert def_card.state == 2
    assert default_card not in player.hand


@pytest.mark.asyncio
async def test_olv(test_db):
    card = cards_schemas.CardCreate(
        code="olv",
        name="Olvidadizo",
        kind=4,
        description="Olvidadizo",
        number_in_card=1,
        playable=True,
    )

    card = cards_crud.create_card(card, 1)
    default_card = cards_schemas.CardCreate(
        code="def",
        name="default",
        kind=0,
        description="default",
        number_in_card=1,
        playable=True,
    )
    for i in range(3):
        default_card = cards_crud.create_card(default_card, 1)
        cards_crud.give_card_to_player(default_card.id, 1, 1)

    full_game = games_crud.get_full_game(1)
    player = players_crud.get_player(1, 1)
    cards_to_discard = [player.hand[i].id for i in range(3)]

    data = {
        "game_id": 1,
        "player_id": 1,
        "card_id": cards_to_discard,
        "panic_card_id": card.id,
    }

    player, game = await apply_olv(data)

    olv_card = cards_crud.get_card(card.id, 1)

    assert olv_card.state == 0
    assert cards_to_discard not in [card.id for card in player.hand]


@pytest.mark.asyncio
async def test_hac_to_cua(test_db):
    players_crud.update_player(
        players_schemas.PlayerUpdate(quarantine=2, table_position=1), 1, 1
    )
    players_crud.update_player(
        players_schemas.PlayerUpdate(
            quarantine=2, alive=True, table_position=2
        ),
        2,
        1,
    )
    players_crud.update_player(
        players_schemas.PlayerUpdate(
            quarantine=2, alive=True, table_position=3
        ),
        3,
        1,
    )
    players_crud.update_player(
        players_schemas.PlayerUpdate(
            quarantine=2, alive=True, table_position=4
        ),
        4,
        1,
    )

    card = cards_schemas.CardCreate(
        code="hac",
        name="Hacha",
        kind=0,
        description="Hacha",
        number_in_card=1,
        playable=True,
    )
    card = cards_crud.create_card(card, 1)
    full_game = games_crud.get_full_game(1)
    player = players_crud.get_player(1, 1)
    destination_player = players_crud.get_player(2, 1)

    obstacle = {"type": "cua", "position": None}

    await apply_hac(full_game, player, destination_player, card, obstacle)

    updated_card = cards_crud.get_card(card.id, 1)
    updated_d_player = players_crud.get_player(2, 1)

    assert updated_card.state == 0
    assert updated_d_player.quarantine == 0


@pytest.mark.asyncio
async def test_hac_to_ptr(test_db):
    card = cards_schemas.CardCreate(
        code="hac",
        name="Hacha",
        kind=0,
        description="Hacha",
        number_in_card=1,
        playable=True,
    )
    card = cards_crud.create_card(card, 1)
    full_game = games_crud.get_full_game(1)
    player = players_crud.get_player(1, 1)
    # the game already has a ptr obstacle in position 1
    # because of test_ptr function
    obstacle = {"type": "ptr", "position": 3}
    o_players = [(player.name, player.table_position) for player in full_game.players]

    try:
        await apply_hac(full_game, player, None, card, obstacle)
    except Exception as e:
        raise e

    updated_card = cards_crud.get_card(card.id, 1)
    game = games_crud.get_full_game(1)
    assert updated_card.state == 0
    assert game.obstacles == []
