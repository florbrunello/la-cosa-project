import random
from src.theThing.games.crud import get_full_game, update_game, get_game
from src.theThing.games.schemas import GameInDB, GameUpdate, GameOut
from src.theThing.cards.crud import (
    remove_card_from_player,
    update_card,
    get_card,
    give_card_to_player,
    get_card_from_deck,
)
from src.theThing.cards.schemas import CardBase, CardUpdate
from src.theThing.players.crud import get_player, update_player
from src.theThing.players.schemas import PlayerBase, PlayerUpdate
from src.theThing.games import socket_handler as sh
from src.theThing.turn.schemas import TurnCreate, TurnOut
from src.theThing.turn.crud import create_turn, update_turn
from src.theThing.games.utils import (
    get_player_in_next_n_places,
    verify_finished_game,
)
from src.theThing.games.socket_handler import (
    send_finished_game_event_to_players,
    send_game_status_to_players,
)

""" 
This file contains the functions to apply the effect of the cards. 
The functions are in a dictionary, which key is the card code. 
IMPORTANT: The parameters must be passed in the following order and types:
    - game: GameInDB
    - player: PlayerBase
    - destination_player: PlayerBase
    - card: CardBase
"""


# Functions implementation
async def apply_lla(
    game: GameInDB,
    player: PlayerBase,
    destination_player: PlayerBase,
    card: CardBase,
):
    # check that the player has 4 cards in hand
    card.state = 0
    destination_player.alive = False
    player = remove_card_from_player(card.id, player.id, game.id)

    # push the changes to the database
    updated_card = update_card(
        CardUpdate(id=card.id, state=card.state), game.id
    )
    updated_destination_player = update_player(
        PlayerUpdate(
            table_position=destination_player.table_position,
            role=destination_player.role,
            alive=destination_player.alive,
            quarantine=destination_player.quarantine,
        ),
        destination_player.id,
        game.id,
    )
    # get the full game again to have the list of players updated
    updated_game = get_full_game(game.id)
    new_exchange_destination = get_player_in_next_n_places(
        updated_game, player.table_position, 1
    )
    new_turn = TurnCreate(
        destination_player_exchange=new_exchange_destination.name
    )
    update_turn(game.id, new_turn)

    # Update the obstacles value, if the dead player was an obstacle
    if destination_player.table_position in game.obstacles:
        alive_players = [
            player.table_position for player in game.players if player.alive
        ]
        alive_players.sort()
        game.obstacles.sort()
        destination_player_index = alive_players.index(
            destination_player.table_position
        )
        game.obstacles.remove(destination_player.table_position)
        game.obstacles.append(alive_players[destination_player_index - 1])
        update_game(game.id, GameUpdate(obstacles=game.obstacles))

    updated_game = get_full_game(game.id)
    response = verify_finished_game(updated_game)
    if response["winners"] is not None:
        await send_game_status_to_players(response["game"].id, response["game"])
        await send_finished_game_event_to_players(game.id, response)
    message = f"{player.name} jugó lanzallamas e incinero a {destination_player.name}"
    return updated_game, message


async def apply_vte(
    game: GameInDB,
    player: PlayerBase,
    destination_player: PlayerBase,
    card: CardBase,
):
    # Remove the card played from the player
    remove_card_from_player(card.id, player.id, game.id)

    # Invert the game play direction
    new_direction = not game.play_direction
    update_game(game.id, GameUpdate(play_direction=new_direction))

    game = get_game(game.id)
    # get the new destination for exchange
    new_exchange_destination = get_player_in_next_n_places(
        game, destination_player.table_position, 1
    )
    new_turn = TurnCreate(
        destination_player_exchange=new_exchange_destination.name
    )
    update_turn(game.id, new_turn)
    updated_game = get_full_game(game.id)
    message = f"Las cosas van para el otro lado! {player.name} invirtió el orden del juego"
    return updated_game, message


async def apply_cdl(
    game: GameInDB,
    player: PlayerBase,
    destination_player: PlayerBase,
    card: CardBase,
):
    card.state = 0
    # swap table position between the players
    player.table_position, destination_player.table_position = (
        destination_player.table_position,
        player.table_position,
    )
    # push the changes to the database
    updated_card = update_card(
        CardUpdate(id=card.id, state=card.state), game.id
    )

    updated_player = update_player(
        PlayerUpdate(table_position=player.table_position), player.id, game.id
    )

    updated_destination_player = update_player(
        PlayerUpdate(table_position=destination_player.table_position),
        destination_player.id,
        game.id,
    )

    game = get_full_game(game.id)
    new_exchange_destination = get_player_in_next_n_places(
        game, updated_player.table_position, 1
    )
    new_turn = TurnCreate(
        owner=updated_player.table_position,
        played_card=card.id,
        destination_player=destination_player.name,
        destination_player_exchange=new_exchange_destination.name,
    )
    update_turn(game.id, new_turn)
    updated_game = get_full_game(game.id)
    message = f"{player.name} jugó cambio de lugar con {destination_player.name}"
    return updated_game, message


async def apply_mvc(
    game: GameInDB,
    player: PlayerBase,
    destination_player: PlayerBase,
    card: CardBase,
):
    card.state = 0
    # swap table position between the players
    player.table_position, destination_player.table_position = (
        destination_player.table_position,
        player.table_position,
    )
    # push the changes to the database
    updated_card = update_card(
        CardUpdate(id=card.id, state=card.state), game.id
    )

    updated_player = update_player(
        PlayerUpdate(table_position=player.table_position), player.id, game.id
    )

    updated_destination_player = update_player(
        PlayerUpdate(table_position=destination_player.table_position),
        destination_player.id,
        game.id,
    )

    game = get_full_game(game.id)
    new_exchange_destination = get_player_in_next_n_places(
        game, updated_player.table_position, 1
    )
    new_turn = TurnCreate(
        owner=updated_player.table_position,
        played_card=card.id,
        destination_player=destination_player.name,
        destination_player_exchange=new_exchange_destination.name,
    )
    update_turn(game.id, new_turn)
    updated_game = get_full_game(game.id)
    message = f"{player.name} jugó Mas vale que corras! a {destination_player.name} y cambiaron sus lugares"
    return updated_game, message


async def apply_ana(
    game: GameInDB,
    player: PlayerBase,
    destination_player: PlayerBase,
    card: CardBase,
):
    card.state = 0
    destination_hand = destination_player.hand

    update_card(CardUpdate(id=card.id, state=card.state), game.id)
    await sh.send_analysis_to_player(
        player.id, destination_hand, destination_player.name
    )
    updated_game = get_full_game(game.id)
    message = f"{player.name} jugó Análisis a {destination_player.name} y vio sus cartas"
    return updated_game, message


async def apply_sos(
    game: GameInDB,
    player: PlayerBase,
    destination_player: PlayerBase,
    card: CardBase,
):
    card.state = 0
    destination_card = random.choice(destination_player.hand)

    update_card(CardUpdate(id=card.id, state=card.state), game.id)
    await sh.send_suspicion_to_player(
        player.id, destination_card, destination_player.name
    )
    updated_game = get_full_game(game.id)
    message = f"{player.name} jugó Sospecha a {destination_player.name} y vio una de sus cartas"
    return updated_game, message


async def apply_whk(
    game: GameInDB,
    player: PlayerBase,
    destination_player: PlayerBase,
    card: CardBase,
):
    card.state = 0
    player_hand = player.hand

    update_card(CardUpdate(id=card.id, state=card.state), game.id)
    await sh.send_whk_to_player(game.id, player.name, player_hand)

    updated_game = get_full_game(game.id)
    if "lco" in [card.code for card in player_hand]:
        message = f"¡Whisky!, {player.name} bebió de más y lo encontraron con La Cosa en la mano!"
    else:
        message = f"{player.name} bebió de más y dejó ver sus cartas a todos!"
    return updated_game, message


async def apply_cua(
    game: GameInDB,
    player: PlayerBase,
    destination_player: PlayerBase,
    card: CardBase,
):
    card.state = 0
    update_card(CardUpdate(id=card.id, state=card.state), game.id)

    update_player(PlayerUpdate(quarantine=2), destination_player.id, game.id)

    updated_game = get_full_game(game.id)

    message = f"{player.name} jugó Cuarentena a {destination_player.name}"
    return updated_game, message


async def apply_ups(
    game: GameInDB,
    player: PlayerBase,
    destination_player: PlayerBase,
    card: CardBase,
):
    card.state = 0
    player_hand = player.hand

    update_card(CardUpdate(id=card.id, state=card.state), game.id)
    await sh.send_ups_to_players(game.id, player.name, player_hand)

    updated_game = get_full_game(game.id)
    if "lco" in [card.code for card in player_hand]:
        message = f"¡Ups!, {player.name} se descuido y lo encontraron con La Cosa en la mano!"
    else:
        message = f"{player.name} se descuido y dejo ver sus cartas a todos!"
    return updated_game, message


async def apply_qen(
    game: GameInDB,
    player: PlayerBase,
    destination_player: PlayerBase,
    card: CardBase,
):
    player_hand = player.hand
    card.state = 0

    update_card(CardUpdate(id=card.id, state=card.state), game.id)
    await sh.send_qen_to_player(player.id, player_hand, destination_player)
    updated_game = get_full_game(game.id)
    message = f"{player.name} tuvo que mostrar sus cartas a {destination_player.name}"
    return updated_game, message


async def apply_cpo(
    game: GameInDB,
    player: PlayerBase,
    destination_player: PlayerBase,
    card: CardBase,
):
    card.state = 0

    # Remove quarantine from all players
    for player in game.players:
        if player.quarantine > 0:
            player.quarantine = 0
            updated_player = update_player(
                PlayerUpdate(quarantine=player.quarantine),
                player.id,
                game.id,
            )
            await sh.send_player_status_to_player(player.id, updated_player)

    update_card(CardUpdate(id=card.id, state=card.state), game.id)
    await sh.send_cpo_to_players(game.id)

    updated_game = get_full_game(game.id)
    message = f"{player.name} jugó Cuerdas podridas y todos se liberaron de su cuarentena!"
    return updated_game, message


async def apply_und(
    game: GameInDB,
    player: PlayerBase,
    destination_player: PlayerBase,
    card: CardBase,
):
    card.state = 0
    # swap table position between the players
    player.table_position, destination_player.table_position = (
        destination_player.table_position,
        player.table_position,
    )
    # push the changes to the database
    updated_card = update_card(
        CardUpdate(id=card.id, state=card.state), game.id
    )

    updated_player = update_player(
        PlayerUpdate(table_position=player.table_position), player.id, game.id
    )

    updated_destination_player = update_player(
        PlayerUpdate(table_position=destination_player.table_position),
        destination_player.id,
        game.id,
    )

    game = get_full_game(game.id)
    new_exchange_destination = get_player_in_next_n_places(
        game, updated_player.table_position, 1
    )
    new_turn = TurnCreate(
        owner=updated_player.table_position,
        played_card=card.id,
        destination_player=destination_player.name,
        destination_player_exchange=new_exchange_destination.name,
    )
    update_turn(game.id, new_turn)
    updated_game = get_full_game(game.id)
    message = f"{player.name} jugó Uno, dos y cambio lugares con {destination_player.name}"
    return updated_game, message


async def apply_sda(
    game: GameInDB,
    player: PlayerBase,
    destination_player: PlayerBase,
    card: CardBase,
):
    card.state = 0
    # swap table position between the players
    player.table_position, destination_player.table_position = (
        destination_player.table_position,
        player.table_position,
    )
    # push the changes to the database
    updated_card = update_card(
        CardUpdate(id=card.id, state=card.state), game.id
    )

    updated_player = update_player(
        PlayerUpdate(table_position=player.table_position), player.id, game.id
    )

    updated_destination_player = update_player(
        PlayerUpdate(table_position=destination_player.table_position),
        destination_player.id,
        game.id,
    )

    game = get_full_game(game.id)
    new_exchange_destination = get_player_in_next_n_places(
        game, updated_player.table_position, 1
    )
    new_turn = TurnCreate(
        owner=updated_player.table_position,
        played_card=card.id,
        destination_player=destination_player.name,
        destination_player_exchange=new_exchange_destination.name,
    )
    update_turn(game.id, new_turn)
    updated_game = get_full_game(game.id)
    message = f"{player.name} jugó Sal de aqui y cambio lugares con {destination_player.name}"
    return updated_game, message


async def apply_trc(
    game: GameInDB,
    player: PlayerBase,
    destination_player: PlayerBase,
    card: CardBase,
):
    card.state = 0
    update_card(CardUpdate(id=card.id, state=card.state), game.id)
    game.obstacles = []
    updated_game = update_game(game.id, GameUpdate(obstacles=game.obstacles))
    message = f"{player.name} jugó Tres, cuatro y se rompieron todas las puertas!"
    return updated_game, message


async def apply_eaf(
    game: GameInDB,
    player: PlayerBase,
    destination_player: PlayerBase,
    card: CardBase,
):
    card.state = 0
    update_card(CardUpdate(id=card.id, state=card.state), game.id)

    # Remove quarantine from all players
    for player_q in game.players:
        updated_player = update_player(
            PlayerUpdate(quarantine=0),
            player_q.id,
            game.id,
        )
        await sh.send_player_status_to_player(player_q.id, updated_player)

    # Remove all locked doors
    game.obstacles = []
    updated_game = update_game(game.id, GameUpdate(obstacles=game.obstacles))
    owner_id = player.id
    # Swap the players by pairs clockwise, starting by the current turn owner
    game_to_update = get_full_game(game.id)
    alive_players = [
        player for player in game_to_update.players if player.alive
    ]
    alive_players.sort(key=lambda x: x.table_position)

    owner = [player for player in alive_players if player.id == owner_id][0]
    owner_index = alive_players.index(owner)

    for i in range(0, len(alive_players) - 1, 2):
        first_player = alive_players[
            (owner_index + i) % len(alive_players)
        ]
        next_player = alive_players[
            (owner_index + i + 1) % len(alive_players)
        ]

        update_player(
            PlayerUpdate(table_position=next_player.table_position),
            first_player.id,
            game.id,
        )
        update_player(
            PlayerUpdate(table_position=first_player.table_position),
            next_player.id,
            game.id,
        )

    updated_player = get_player(owner_id, game.id)
    # Update the turn accordingly
    game = get_full_game(game.id)
    new_exchange_destination = get_player_in_next_n_places(
        game, updated_player.table_position, 1
    )
    turn_owner = [player.table_position for player in game.players if player.id == owner_id][0]
    new_turn = TurnCreate(
        owner=turn_owner,
        played_card=card.id,
        destination_player=destination_player.name,
        destination_player_exchange=new_exchange_destination.name,
    )
    update_turn(game.id, new_turn)
    # Update the turn
    updated_game = get_full_game(game.id)
    message = f"A bailar! {player.name} jugó ¿Es aqui la fiesta? y cambiaron todos sus lugares. Ademas, rompió todas las puertas y cuarentenas!"
    return updated_game, message


async def just_discard(
    game: GameInDB,
    player: PlayerBase,
    destination_player: PlayerBase,
    card: CardBase,
):
    # other cards
    card.state = 0
    player = remove_card_from_player(card.id, player.id, game.id)

    # push the changes to the database
    updated_card = update_card(
        CardUpdate(id=card.id, state=card.state), game.id
    )


async def apply_ptr(
    game: GameInDB,
    player: PlayerBase,
    destination_player: PlayerBase,
    card: CardBase,
):
    """The values in obstacles[] are interpreted as: a door exists between the value
    (player_position) and the nearest alive player positioned on the right side of player_position,
    i.e. player_position represents the left side of the door."""
    player_position = player.table_position
    destination_player_position = destination_player.table_position
    alive_players = [
        player.table_position for player in game.players if player.alive
    ]
    alive_players.sort()
    # Set the door according to the position of the players
    if (
        player_position == alive_players[0]
        and destination_player_position == alive_players[-1]
    ) or (
        player_position == alive_players[-1]
        and destination_player_position == alive_players[0]
    ):
        game.obstacles.append(alive_players[-1])
    elif player_position < destination_player_position:
        game.obstacles.append(player_position)
    elif player_position > destination_player_position:
        game.obstacles.append(destination_player_position)

    update_game(game.id, GameUpdate(obstacles=game.obstacles))
    card.state = 0
    player = remove_card_from_player(card.id, player.id, game.id)

    # push the changes to the database
    updated_card = update_card(
        CardUpdate(id=card.id, state=card.state), game.id
    )
    updated_game = get_full_game(game.id)
    message = f"{player.name} colocó una puerta entre frente a {destination_player.name}"
    return updated_game, message



effect_applications = {
    "lla": apply_lla,
    "vte": apply_vte,
    "cdl": apply_cdl,
    "mvc": apply_mvc,
    "ana": apply_ana,
    "sos": apply_sos,
    "whk": apply_whk,
    "cua": apply_cua,
    "ups": apply_ups,
    "qen": apply_qen,
    "cpo": apply_cpo,
    "und": apply_und,
    "sda": apply_sda,
    "trc": apply_trc,
    "eaf": apply_eaf,
    "ptr": apply_ptr,
    "default": just_discard,
}


async def apply_ate(
    game: GameInDB,
    player: PlayerBase,
    destination_player: PlayerBase,
    card: CardBase,
):
    card.state = 0

    # push the changes to the database
    updated_card = update_card(
        CardUpdate(id=card.id, state=card.state), game.id
    )

    card_to_send = player.card_to_exchange
    update_player(PlayerUpdate(card_to_exchange=None), player.id, game.id)

    update_turn(game.id, TurnCreate(state=5))
    await sh.send_ate_to_player(
        game.id, player, destination_player, card_to_send
    )

    updated_game = get_full_game(game.id)
    message = f"{player.name} se defendio del intercambio usando Aterrador!"
    return updated_game, message


async def apply_ngs(
    game: GameInDB,
    player: PlayerBase,
    destination_player: PlayerBase,
    card: CardBase,
):
    card.state = 0

    # push the changes to the database
    updated_card = update_card(
        CardUpdate(id=card.id, state=card.state), game.id
    )

    update_player(PlayerUpdate(card_to_exchange=None), player.id, game.id)

    update_turn(game.id, TurnCreate(state=5))

    updated_game = get_full_game(game.id)
    message = f"{player.name} dijo No Gracias! y rechazo el intercambio"
    return updated_game, message


async def apply_fal(
    game: GameInDB,
    player: PlayerBase,
    destination_player: PlayerBase,
    card: CardBase,
):
    card.state = 0

    # push the changes to the database
    updated_card = update_card(
        CardUpdate(id=card.id, state=card.state), game.id
    )

    update_player(
        PlayerUpdate(card_to_exchange=None), destination_player.id, game.id
    )

    game = get_game(game.id)
    new_dest = get_player_in_next_n_places(
        game, destination_player.table_position, 1
    )
    update_turn(
        game.id, TurnCreate(state=4, destination_player_exchange=new_dest.name)
    )
    message = f"{player.name} se defendio usando Fallaste!, ahora {new_dest.name} debe intercambiar"
    game = get_full_game(game.id)
    return game, message

exchange_defense = {
    "ate": apply_ate,
    "ngs": apply_ngs,
    "fal": apply_fal,
    "default": just_discard,
}
